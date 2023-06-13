import os
import cv2
import pytesseract
import mysql.connector

# Informasi koneksi database
host = "localhost"
username = "root"  # Ganti dengan nama pengguna database Anda
password = ""  # Ganti dengan kata sandi database Anda
database = "dbhasil"  # Ganti dengan nama database yang telah Anda buat

# Membuat koneksi ke database
conn = mysql.connector.connect(
    host=host,
    user=username,
    password=password,
    database=database
)

# Memeriksa koneksi
if conn.is_connected():
    print("Koneksi berhasil.")

    # akses ke folder yang berisi hasil gambar
    folder_path = 'C:/Users/hp/Documents/Proposal PA/preprocessing/Bahan Gambar Meteran'

    # Loop untuk membaca setiap file gambar di folder
    for filename in os.listdir(folder_path):

        # Mengabaikan file yang bukan gambar
        if filename.endswith('.jpeg') or filename.endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Grey.jpg", gray)

            thres = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            cv2.imshow("threshold.jpg", thres)

            contours =  cv2.findContours(thres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else cents[1]
            contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h>20 and w > 20 :
                    roi = img[y:y+h, x:x+w]
                    cv2.rectangle(img, (x, y), (x + w, y + h), (36,255,12),2 )
                    cv2.imshow('roi', roi)
                    text = pytesseract.image_to_string(roi, config=r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789')
                    print('File:', filename)
                    print("Hasil output:", text)

                    # Menyimpan hasil OCR ke dalam database
                    cursor = conn.cursor()
                    insert_query = "INSERT INTO tr_tagihan (filename, kwh_before) VALUES (%s, %s)"
                    values = (filename, text)
                    cursor.execute(insert_query, values)
                    conn.commit()
                    print("Data berhasil disimpan ke dalam database.")

                    cursor.close()

else:
    print("Koneksi gagal.")

conn.close()
