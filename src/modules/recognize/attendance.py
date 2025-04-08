import sys
from datetime import datetime
from pathlib import Path

# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent.parent)  # Lên 3 cấp để tới src
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Custom modules
from database import handleDB
from modules.constants_cus import MIN_CHECKOUT_DELAY


def attendance(ui, best_match_id, best_match_name):
    # Dictionary để lưu thời gian nhận diện gần nhất
    last_recognition_time = {}
    stt_counter = len(ui.tree.get_children()) + 1  # Đếm STT từ số bản ghi hiện có trong bảng

    # Lấy thời gian hiện tại
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    current_date = current_time.date()

    # Xử lý chấm công khi nhận diện thành công
    # best_match_id = int(best_match_id)
    last_time = last_recognition_time.get(best_match_id)

    # Tránh nhận diện liên tục (trong khoảng 10 giây)
    if last_time is None or (current_time - last_time).total_seconds() > 10:
        last_attendance = handleDB.handle.get_last_attendance_in_date(best_match_id)
        
        print(f"last_attendance: {last_attendance}")

        if last_attendance is None:  # Chưa có bản ghi nào trong ngày hiện tại
            # Check-in mới
            handleDB.handle.write_check_in_to_db(best_match_id, current_time_str)
            print(f"Check-in: {best_match_id} at {current_time_str}")
            # Thêm vào dòng đầu tiên của bảng trên giao diện
            ui.add_attendance_record(
                stt_counter,
                f"NV{best_match_id:03d}",
                best_match_id,
                current_time.strftime("%H:%M:%S")
            )
            stt_counter += 1

            print(f"Check-in thành công cho {best_match_id}-{best_match_name}")
            # return tuple 
            return True, f"Check-in thành công cho {best_match_id}-{best_match_name}"

        elif last_attendance['check_out'] is None:  # Đã check-in nhưng chưa check-out
            # Check-out
            last_check_in = last_attendance['check_in']
            time_diff = (current_time - last_check_in).total_seconds()

            # Kiểm tra thời gian check-out tối thiểu sau 1 giờ
            if time_diff >= MIN_CHECKOUT_DELAY:
                handleDB.handle.update_check_out_to_db(best_match_id, current_time_str, current_date)
                print(f"Check-out: {best_match_id} at {current_time_str}")
                # Cập nhật bảng trên giao diện (tìm bản ghi và thêm thời gian check-out)
                for item in ui.tree.get_children():
                    values = ui.tree.item(item, "values")
                    if values[1] == f"NV{best_match_id:03d}" and values[4] == "":
                        ui.tree.set(item, "Ra", current_time.strftime("%H:%M:%S"))
                        break
                print(f"Check-out thành công cho {best_match_id}-{best_match_name}")
                # return tuple (True, f"Check-out thành công cho {best_match_name}")
                return True, f"Check-out thành công cho {best_match_id}-{best_match_name}"
            else:
                print
                print(f"Chưa đủ {MIN_CHECKOUT_DELAY // 3600} giờ để check-out cho {best_match_id}-{best_match_name}")
                # Return tuple (False, error_message)
                return False, f"Chưa đủ {MIN_CHECKOUT_DELAY // 3600} giờ để check-out cho {best_match_id}-{best_match_name}"
        else:
            print(f"Đã hoàn tất check-in và check-out cho {best_match_id}-{best_match_name} trong ngày hôm nay")
            # Return tuple (False, error_message)
            return False, f"Đã hoàn tất check-in và check-out cho {best_match_id}-{best_match_name} trong ngày hôm nay"

        last_recognition_time[best_match_id] = current_time

# def attendance (ui, best_match_name):
#     # Dictionary để lưu thời gian nhận diện gần nhất
#     last_recognition_time = {}
#     stt_counter = len(ui.tree.get_children()) + 1  # Đếm STT từ số bản ghi hiện có trong bảng

#     # Lấy thời gian hiện tại
#     current_time = datetime.now()
#     current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

#     # Xử lí chấm công khi nhận diện thành công:
#     """ Ngày hiện tại: 
#     1. Chưa check-in thì check-in
#     2. Đã check-in thì check-out
#         - Điều kiện check-out:
#             - Thời gian check-out lớn hơn MIN_CHECKOUT_DELAY
#             (Thời gian check-out tối thiểu là 1 giờ, sau check-in)
#     """
#     emp_id = int(best_match_name)
#     last_time = last_recognition_time.get(emp_id)

#     # Tránh nhận diện liên tục (trong khoảng 10 giây)
#     if last_time is None or (current_time - last_time).total_seconds() > 10:
#         last_attendance = handleDB.handle.get_last_attendance_in_date(emp_id)
        
#         if last_attendance is None or last_attendance['check_out'] is not None:
#             # Check-in mới
#             handleDB.handle.write_check_in_to_db(emp_id, current_time_str)
#             print(f"Check-in: {emp_id} at {current_time_str}")
#             # Thêm vào dòng đầu tiên của bảng trên giao diện
#             ui.add_attendance_record(
#                 stt_counter,
#                 f"NV{emp_id:03d}",
#                 best_match_name,
#                 current_time.strftime("%H:%M:%S")
#             )
#             stt_counter += 1
#         else:
#             # Check-out
#             last_check_in = last_attendance['check_in']
#             time_diff = (current_time - last_check_in).total_seconds()
            
#             # Kiểm tra thời gian check-out tối thiểu sau 1 giờ
#             if time_diff >= MIN_CHECKOUT_DELAY:
#                 handleDB.handle.update_check_out_to_db(emp_id, current_time_str, last_attendance['date'])
#                 print(f"Check-out: {emp_id} at {current_time_str}")
#                 # Cập nhật bảng trên giao diện (tìm bản ghi và thêm thời gian check-out)
#                 for item in ui.tree.get_children():
#                     values = ui.tree.item(item, "values")
#                     if values[1] == f"NV{emp_id:03d}" and values[4] == "":
#                         ui.tree.set(item, "Ra", current_time.strftime("%H:%M:%S"))
#                         break
#             else:
#                 print(f"Chưa đủ {MIN_CHECKOUT_DELAY // 3600} giờ để check-out cho {emp_id}")
        
#         last_recognition_time[emp_id] = current_time


