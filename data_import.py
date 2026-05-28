import os
import time
import math
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from database import get_db_connection

# 1. Environment Logging Control
LOG_LEVEL = logging.DEBUG if os.environ.get('FLASK_ENV') == 'development' else logging.INFO
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataIngestionSaaS")

# SaaS Master Configs
CHUNK_SIZE = 10000

def clean_value(val):
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (np.int64, np.float64)):
        if math.isnan(val):
            return None
        return val.item()
    if isinstance(val, str):
        return val.strip()
    return val

def validate_columns(chunk, required_columns):
    missing_cols = [col for col in required_columns if col not in chunk.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    return True, ""

def process_multi_upload(users_path, products_path, orders_path, business_id, dataset_id, clear_data=False, column_mappings=None):
    start_time = time.perf_counter()
    logger.info(f"Initiating Ultra-Fast MongoDB Bulk Pipeline for Business {business_id}.")
    
    db = get_db_connection()
    if db is None:
        logger.error("MongoDB connection securely denied.")
        return {"status": "failed", "message": "Database connection failed globally", "error_code": "DB_CONNECTION_ERROR"}
        
    total_rows = inserted_rows = failed_rows = 0

    try:
        # Phase 1: Header Validation
        u_header = pd.read_csv(users_path, nrows=0)
        p_header = pd.read_csv(products_path, nrows=0)
        o_header = pd.read_csv(orders_path, nrows=0)
        
        u_header.columns = u_header.columns.str.strip().str.lower()
        p_header.columns = p_header.columns.str.strip().str.lower()
        o_header.columns = o_header.columns.str.strip().str.lower()
        
        # Apply column mappings to headers for validation
        if column_mappings:
            import json
            if isinstance(column_mappings, str):
                try: column_mappings = json.loads(column_mappings)
                except Exception as ex: logger.warning(f"Failed to parse column mappings string: {ex}")
            
            def rename_headers(cols, mapping):
                if not mapping:
                    return cols
                # Create reverse mapping: actual CSV column (value) -> expected standard column (key)
                rev_mapping = {str(v).strip().lower(): str(k).strip().lower() for k, v in mapping.items() if v}
                return [rev_mapping.get(c, c) for c in cols]

            if isinstance(column_mappings, dict):
                u_header.columns = rename_headers(u_header.columns, column_mappings.get('users'))
                p_header.columns = rename_headers(p_header.columns, column_mappings.get('products'))
                o_header.columns = rename_headers(o_header.columns, column_mappings.get('orders'))
        
        o_req = ['order_id', 'user_id', 'product_id', 'quantity', 'total_amount']
        if 'order_date' in o_header.columns:
            o_req.append('order_date')
        elif 'date' in o_header.columns:
            o_req.append('date')
        else:
            o_req.append('order_date')

        for df_h, name, req in [
            (u_header, 'Users', ['user_id', 'name'] if 'name' in u_header.columns else ['user_id', 'user_name']),
            (p_header, 'Products', ['product_id', 'product_name'] if 'product_name' in p_header.columns else ['product_id', 'name']),
            (o_header, 'Orders', o_req)
        ]:
            valid, msg = validate_columns(df_h, req)
            if not valid:
                try:
                    db.datasets.update_one({"id": int(dataset_id)}, {"$set": {"status": "failed"}})
                except: pass
                return {"status": "failed", "message": f"{name} CSV Format strictly failed check: {msg}", "error_code": "CSV_VALIDATION_ERROR"}

        # Phase 2: Clear Data if requested
        if clear_data:
            logger.info(f"Clearing previous data for Business {business_id} in MongoDB.")
            db.users.delete_many({"business_id": int(business_id)})
            db.products.delete_many({"business_id": int(business_id)})
            db.orders.delete_many({"business_id": int(business_id)})
            
        db.datasets.update_one({"id": int(dataset_id)}, {"$set": {"status": "processing"}})

        # Phase 3: Processing Chunks and Bulk Inserting to MongoDB
        def import_csv(file_path, collection_name, row_mapper):
            nonlocal total_rows, inserted_rows, failed_rows
            
            for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
                chunk_len = len(chunk)
                total_rows += chunk_len
                chunk.columns = chunk.columns.str.strip().str.lower()
                
                # Apply column mappings to chunk before processing if present
                if column_mappings and isinstance(column_mappings, dict) and collection_name in column_mappings:
                    mapping = column_mappings[collection_name]
                    rev_mapping = {str(v).strip().lower(): str(k).strip().lower() for k, v in mapping.items() if v}
                    chunk.rename(columns=rev_mapping, inplace=True)
                
                if collection_name == 'users' and 'user_name' in chunk.columns and 'name' not in chunk.columns:
                    chunk.rename(columns={'user_name': 'name'}, inplace=True)
                if collection_name == 'products' and 'name' in chunk.columns and 'product_name' not in chunk.columns:
                    chunk.rename(columns={'name': 'product_name'}, inplace=True)
                if collection_name == 'orders' and 'date' in chunk.columns and 'order_date' not in chunk.columns:
                    chunk.rename(columns={'date': 'order_date'}, inplace=True)

                documents = []
                for row in chunk.to_dict('records'):
                    try:
                        doc = row_mapper(row)
                        if doc:
                            documents.append(doc)
                    except Exception as parse_err:
                        failed_rows += 1
                        logger.error(f"Row mapping failure: {parse_err}")
                        db.upload_errors.insert_one({
                            "dataset_id": int(dataset_id),
                            "table_name": collection_name,
                            "error_message": str(parse_err)[:250],
                            "raw_data": str(row)[:500],
                            "created_at": datetime.now()
                        })

                if documents:
                    try:
                        db[collection_name].insert_many(documents, ordered=False)
                        inserted_rows += len(documents)
                    except Exception as bulk_err:
                        # Find out successful vs failed count if write errors occur
                        failed_rows += len(documents)
                        logger.error(f"Bulk insertion failed in {collection_name}: {bulk_err}")
                        db.upload_errors.insert_one({
                            "dataset_id": int(dataset_id),
                            "table_name": collection_name,
                            "error_message": str(bulk_err)[:250],
                            "created_at": datetime.now()
                        })

        def map_user(row):
            return {
                "user_id": str(clean_value(row.get('user_id', ''))),
                "business_id": int(business_id),
                "dataset_id": int(dataset_id),
                "name": str(row.get('name', '')).strip(),
                "city": clean_value(row.get('city')),
                "state": clean_value(row.get('state')),
                "country": str(row.get('country', '')).strip(),
                "age": int(clean_value(row.get('age')) or 0) if clean_value(row.get('age')) else None,
                "gender": str(row.get('gender', '')).strip()
            }
            
        def map_product(row):
            import random
            price = clean_value(row.get('price')) or 0.0
            brand = str(clean_value(row.get('brand'))) if 'brand' in row and not pd.isna(row.get('brand')) else 'Unknown'
            discount = clean_value(row.get('discount')) or 0.0
            
            # Extract stock, fallback to random value between 10 and 150
            stock = clean_value(row.get('stock'))
            if stock is None or pd.isna(stock):
                stock = random.randint(10, 150)
            else:
                try: stock = int(stock)
                except: stock = random.randint(10, 150)
                
            # Extract cost price, fallback to price * uniform(0.6, 0.75)
            cost_price = clean_value(row.get('cost_price'))
            if cost_price is None or pd.isna(cost_price):
                cost_price = float(price) * random.uniform(0.6, 0.75)
            else:
                try: cost_price = float(cost_price)
                except: cost_price = float(price) * random.uniform(0.6, 0.75)
                
            return {
                "product_id": str(clean_value(row.get('product_id', ''))),
                "business_id": int(business_id),
                "dataset_id": int(dataset_id),
                "product_name": str(row.get('product_name', '')).strip(),
                "category": str(row.get('category', '')).strip(),
                "price": float(price),
                "brand": brand,
                "discount": float(discount),
                "stock": int(stock),
                "cost_price": float(cost_price)
            }
            
        def map_order(row):
            raw_date = row.get('order_date')
            dt = '2024-01-01'
            if not pd.isna(raw_date):
                try: dt = pd.to_datetime(raw_date).strftime('%Y-%m-%d')
                except: pass
            
            try:
                dt_obj = datetime.strptime(dt, '%Y-%m-%d')
            except:
                dt_obj = datetime(2024, 1, 1)

            return {
                "order_id": str(clean_value(row.get('order_id', ''))),
                "business_id": int(business_id),
                "dataset_id": int(dataset_id),
                "user_id": str(clean_value(row.get('user_id', ''))),
                "product_id": str(clean_value(row.get('product_id', ''))),
                "quantity": int(clean_value(row.get('quantity')) or 0),
                "order_date": dt_obj,
                "total_amount": float(clean_value(row.get('total_amount')) or 0.0),
                "payment_method": str(row.get('payment_method', 'Unknown')).strip(),
                "order_status": str(row.get('order_status', 'Completed')).strip()
            }

        logger.info("Importing users...")
        import_csv(users_path, 'users', map_user)
        logger.info("Importing products...")
        import_csv(products_path, 'products', map_product)
        logger.info("Importing orders...")
        import_csv(orders_path, 'orders', map_order)

        proc_time = round(time.perf_counter() - start_time, 2)
        final_status = 'completed' if (failed_rows == 0 or inserted_rows > 0) else 'failed'
        if failed_rows > 0 and inserted_rows == 0:
            final_status = 'failed'

        db.datasets.update_one(
            {"id": int(dataset_id)},
            {"$set": {
                "status": final_status,
                "total_rows": int(total_rows),
                "inserted_rows": int(inserted_rows),
                "failed_rows": int(failed_rows),
                "processing_time": float(proc_time)
            }}
        )
        
        logger.info(f"Dataset {dataset_id} import complete. Status: {final_status}")
        return {
            "status": final_status,
            "total_rows": total_rows,
            "inserted": inserted_rows,
            "failed": failed_rows,
            "processing_time_sec": proc_time,
            "error_limit_reached": False
        }
        
    except Exception as e:
        logger.error(f"Critical Native Pipe Exception. Error: {e}")
        try: 
            db.datasets.update_one({"id": int(dataset_id)}, {"$set": {"status": "failed"}})
        except: pass
        
        return {
            "status": "failed",
            "message": str(e),
            "error_code": "CRITICAL_PIPELINE_ERROR"
        }
        
    finally:
        # Clean original upload artifacts
        for fp in [users_path, products_path, orders_path]:
            if fp and os.path.exists(fp):
                try: os.remove(fp)
                except OSError as fs_err: logger.warning(f"File structural cleanup blocked: {fs_err}")
