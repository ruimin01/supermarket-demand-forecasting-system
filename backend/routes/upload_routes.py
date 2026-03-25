from flask import Blueprint, request
from utils.response import success_response, error_response
from utils.auth_helper import user_has_permission
from services.upload_service import save_upload_record
from services.import_service import import_necessity_csv, import_vegetable_csv
import json
import pandas as pd
from io import StringIO

upload_bp = Blueprint("upload_bp", __name__)

@upload_bp.route("/upload-sales", methods=["POST"])
def upload_sales():
    try:
        current_user_raw = request.form.get("currentUser")
        if not current_user_raw:
            return error_response("current user is required", 401)

        current_user = json.loads(current_user_raw)

        if not user_has_permission(current_user, "can_upload"):
            return error_response("no permission to upload data", 403)

        if "file" not in request.files:
            return error_response("file is required", 400)

        file_storage = request.files["file"]

        if not file_storage.filename:
            return error_response("invalid file name", 400)

        filename = file_storage.filename.lower()

        if "vegetable" in filename:
            dataset_type = "vegetable"
            prediction_category = "stable_short_term"
        elif "necessity" in filename:
            dataset_type = "necessity"
            prediction_category = "high_volatility_short_term"
        else:
            dataset_type = "custom"
            prediction_category = None

        max_rows_raw = request.form.get("maxRows")
        max_rows = int(max_rows_raw) if max_rows_raw else None

        file_bytes = file_storage.read()
        if not file_bytes:
            return error_response("uploaded file is empty", 400)

        try:
            file_content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            file_content = file_bytes.decode("latin1")

        df = pd.read_csv(StringIO(file_content))
        row_count = int(len(df))

        upload_id = save_upload_record(
            file_name=file_storage.filename,
            dataset_type=dataset_type,
            upload_user_id=current_user["user_id"],
            row_count=row_count,
            file_path=None,
            status="completed",
            remarks="CSV uploaded successfully"
        )

        # 先只支持 vegetable / necessity
        if dataset_type == "vegetable":
            import_result = import_vegetable_csv(
                df=df,
                file_id=upload_id,
                prediction_category=prediction_category,
                max_rows=max_rows
            )
        elif dataset_type == "necessity":
            import_result = import_necessity_csv(
                df=df,
                file_id=upload_id,
                prediction_category=prediction_category,
                max_rows=max_rows
            )
        else:
            import_result = {
                "inserted_products": 0,
                "inserted_sales_records": 0
            }

        return success_response({
            "file_id": upload_id,
            "filename": file_storage.filename,
            "dataset_type": dataset_type,
            "upload_user_id": current_user["user_id"],
            "row_count": row_count,
            "import_result": import_result,
            "status": "uploaded"
        }, "file uploaded and imported")

    except Exception as e:
        print("Upload error:", str(e))
        return error_response(f"upload failed: {str(e)}", 500)
# from flask import Blueprint, request
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission
# from services.upload_service import save_upload_record
# import json
# import pandas as pd
# from io import StringIO

# upload_bp = Blueprint("upload_bp", __name__)

# @upload_bp.route("/upload-sales", methods=["POST"])
# def upload_sales():
#     try:
#         current_user_raw = request.form.get("currentUser")
#         if not current_user_raw:
#             return error_response("current user is required", 401)

#         current_user = json.loads(current_user_raw)

#         if not user_has_permission(current_user, "can_upload"):
#             return error_response("no permission to upload data", 403)

#         if "file" not in request.files:
#             return error_response("file is required", 400)

#         file_storage = request.files["file"]

#         if not file_storage.filename:
#             return error_response("invalid file name", 400)

#         filename = file_storage.filename.lower()

#         if "vegetable" in filename:
#             dataset_type = "vegetable"
#         elif "necessity" in filename:
#             dataset_type = "necessity"
#         else:
#             dataset_type = "custom"

#         # 读取 CSV 内容
#         file_bytes = file_storage.read()

#         if not file_bytes:
#             return error_response("uploaded file is empty", 400)

#         # 优先尝试 utf-8，失败再尝试 latin1
#         try:
#             file_content = file_bytes.decode("utf-8")
#         except UnicodeDecodeError:
#             file_content = file_bytes.decode("latin1")

#         # 读入 pandas
#         df = pd.read_csv(StringIO(file_content))
#         row_count = int(len(df))

#         print("Received file:", file_storage.filename)
#         print("Dataset type:", dataset_type)
#         print("Row count:", row_count)
#         print("Current user:", current_user)

#         upload_id = save_upload_record(
#             file_name=file_storage.filename,
#             dataset_type=dataset_type,
#             upload_user_id=current_user["user_id"],
#             row_count=row_count,
#             file_path=None,
#             status="completed",
#             remarks="CSV uploaded successfully"
#         )

#         return success_response({
#             "file_id": upload_id,
#             "filename": file_storage.filename,
#             "dataset_type": dataset_type,
#             "upload_user_id": current_user["user_id"],
#             "row_count": row_count,
#             "status": "uploaded"
#         }, "file uploaded")

#     except Exception as e:
#         print("Upload error:", str(e))
#         return error_response(f"upload failed: {str(e)}", 500)
    







# from flask import Blueprint, request
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission
# from services.upload_service import save_upload_record
# import json
# import pandas as pd
# from io import StringIO

# upload_bp = Blueprint("upload_bp", __name__)

# @upload_bp.route("/upload-sales", methods=["POST"])
# def upload_sales():
#     current_user_raw = request.form.get("currentUser")
#     if not current_user_raw:
#         return error_response("current user is required", 401)

#     current_user = json.loads(current_user_raw)

#     if not user_has_permission(current_user, "can_upload"):
#         return error_response("no permission to upload data", 403)

#     if "file" not in request.files:
#         return error_response("file is required", 400)

#     file_storage = request.files["file"]

#     if not file_storage.filename:
#         return error_response("invalid file name", 400)

#     filename = file_storage.filename.lower()

#     if "vegetable" in filename:
#         dataset_type = "vegetable"
#     elif "necessity" in filename:
#         dataset_type = "necessity"
#     else:
#         dataset_type = "custom"

#     # 读取 CSV 内容并统计行数
#     try:
#         file_content = file_storage.read().decode("utf-8")
#         df = pd.read_csv(StringIO(file_content))
#         row_count = len(df)
#     except Exception as e:
#         return error_response(f"failed to read csv file: {str(e)}", 400)

#     upload_id = save_upload_record(
#         file_name=file_storage.filename,
#         dataset_type=dataset_type,
#         upload_user_id=current_user["user_id"],
#         row_count=row_count,
#         file_path=None,
#         status="completed",
#         remarks="CSV uploaded successfully"
#     )

#     return success_response({
#         "file_id": upload_id,
#         "filename": file_storage.filename,
#         "dataset_type": dataset_type,
#         "upload_user_id": current_user["user_id"],
#         "row_count": row_count,
#         "status": "uploaded"
#     }, "file uploaded")




# from flask import Blueprint, request
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission
# from services.upload_service import save_upload_record
# import json
# import os

# upload_bp = Blueprint("upload_bp", __name__)

# @upload_bp.route("/upload-sales", methods=["POST"])
# def upload_sales():
#     current_user_raw = request.form.get("currentUser")
#     print("current_user_raw =", current_user_raw)

#     if not current_user_raw:
#         return error_response("current user is required", 401)

#     current_user = json.loads(current_user_raw)
#     print("current_user =", current_user)

#     if not user_has_permission(current_user, "can_upload"):
#         return error_response("no permission to upload data", 403)

#     if "file" not in request.files:
#         return error_response("file is required", 400)

#     file_storage = request.files["file"]
#     print("received file =", file_storage.filename)

#     filename_lower = file_storage.filename.lower()

#     if "vegetable" in filename_lower:
#         dataset_type = "vegetable"
#     elif "necessity" in filename_lower:
#         dataset_type = "necessity"
#     else:
#         dataset_type = "custom"

#     upload_id = save_upload_record(
#         file_name=file_storage.filename,
#         dataset_type=dataset_type,
#         upload_user_id=current_user["user_id"],
#         row_count=0,
#         file_path=None,
#         status="completed",
#         remarks="Manual upload test"
#     )

#     print("saved upload_id =", upload_id)

#     return success_response({
#         "file_id": upload_id,
#         "filename": file_storage.filename,
#         "dataset_type": dataset_type,
#         "upload_user_id": current_user["user_id"],
#         "status": "uploaded"
#     }, "file uploaded")





# @upload_bp.route("/upload-sales", methods=["POST"])
# def upload_sales():
#     current_user_raw = request.form.get("currentUser")
#     if not current_user_raw:
#         return error_response("current user is required", 401)

#     current_user = json.loads(current_user_raw)

#     if not user_has_permission(current_user, "can_upload"):
#         return error_response("no permission to upload data", 403)

#     if "file" not in request.files:
#         return error_response("file is required", 400)

#     file_storage = request.files["file"]

#     if not file_storage.filename:
#         return error_response("invalid file name", 400)

#     filename = file_storage.filename.lower()

#     # 根据文件名粗略判断数据类型
#     if "vegetable" in filename:
#         dataset_type = "vegetable"
#     elif "necessity" in filename:
#         dataset_type = "necessity"
#     else:
#         dataset_type = "custom"

#     # 这里只是先记录上传行为，不强制保存真实文件到磁盘
#     # 如果你后面想保存真实文件，可以加 file_storage.save(...)
#     upload_id = save_upload_record(
#         file_name=file_storage.filename,
#         dataset_type=dataset_type,
#         upload_user_id=current_user["user_id"],
#         row_count=0,
#         file_path=None,
#         status="completed",
#         remarks="Manual upload test"
#     )

#     return success_response({
#         "file_id": upload_id,
#         "filename": file_storage.filename,
#         "dataset_type": dataset_type,
#         "upload_user_id": current_user["user_id"],
#         "status": "uploaded"
#     }, "file uploaded")
# .............................
# from flask import Blueprint, request
# from services.upload_service import upload_sales_file_service
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission
# import json

# upload_bp = Blueprint("upload_bp", __name__)

# @upload_bp.route("/upload-sales", methods=["POST"])
# def upload_sales():
#     current_user_raw = request.form.get("currentUser")
#     if not current_user_raw:
#         return error_response("current user is required", 401)

#     current_user = json.loads(current_user_raw)

#     if not user_has_permission(current_user, "can_upload"):
#         return error_response("no permission to upload data", 403)

#     if "file" not in request.files:
#         return error_response("file is required", 400)

#     file_storage = request.files["file"]
#     result = upload_sales_file_service(file_storage)
#     return success_response(result, "file uploaded")