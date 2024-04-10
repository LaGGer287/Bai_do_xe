from ultralytics import YOLO
import cv2
from read import detect_license_plate
import time


def detect_and_process_license_plate():
    #license_plate_text = None
    # Khởi tạo YOLO detector
    license_plate_detector = YOLO('license_plate_detector.pt')
    cap = cv2.VideoCapture(0) 
    ret = True
    capture_image = False  # Cờ để kiểm soát việc chụp ảnh
    processing_image = False  # Cờ để kiểm soát quá trình xử lý ảnh
    start_time = 0  # Thời điểm bắt đầu đếm

    while ret:
        ret, frame = cap.read()
        if ret:
            if not capture_image and not processing_image:
                # Phát hiện biển số và xử lý ảnh
                license_plates = license_plate_detector(frame)[0]
                if len(license_plates) > 0:
                    capture_image = True
                    start_time = time.time()  # Bắt đầu đếm thời gian
                    
            if capture_image:
                current_time = time.time()
                if current_time - start_time >= 5:  # Chờ 5 giây trước khi chụp ảnh
                    # Phát hiện biển số và xử lý ảnh
                    license_plates = license_plate_detector(frame)[0]
                    for license_plate in license_plates.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = license_plate

                        license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                        
                        #cv2.imshow('Original Crop', license_plate_crop)
                        filename = 'crop.jpg'
                        cv2.imwrite(filename, license_plate_crop)
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        license_plate_crop_gray_thresh = cv2.threshold(license_plate_crop_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                        
                        # Lưu ảnh biển số vào một tệp tin
                        filename = 'test.jpg'
                        cv2.imwrite(filename, license_plate_crop_gray_thresh)
                        #print(f"Đã lưu ảnh của biển số vào '{filename}'")

                        # Sử dụng hàm detect_license_plate để đọc biển số từ ảnh đã chụp
                        license_plate_text = detect_license_plate(filename)
                        print("Biển số:", license_plate_text)
                        
                        capture_image = False  # Đặt cờ trở lại False sau khi đã xử lý xong ảnh
                        processing_image = True  # Đặt cờ để xử lý ảnh thành True
                        yield  license_plate_text  # Trả về giá trị biển số đã nhận dạng
                
            if processing_image:
                current_time = time.time()
                if current_time - start_time >= 5:  # Chờ 5 giây trước khi tiếp tục phát hiện biển số
                    processing_image = False
                    start_time = 0  # Đặt lại thời gian bắt đầu đếm
            
            cv2.imshow('Video', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    #return license_plate_texts

# Thử nghiệm hàm
if __name__ == "__main__":
    generator = detect_and_process_license_plate()  # Lưu trữ generator
    for license_plate in generator:  # Lặp qua từng giá trị của generator
        print("Detected License Plate:", license_plate)  # In ra biển số đã nhận dạng
    
