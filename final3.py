from tkinter import *
from PIL import ImageTk, Image
import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime
import pandas as pd
import webbrowser
from email.message import EmailMessage
import smtplib

root = Tk()
root.configure(background="White")

root.title("Attendance system")

img =Image.open('C:\\Users\\cjaga\\Desktop\\face recognition system\\face-rec.jpg')
resized=img.resize((1350,800), Image.LANCZOS)
bg = ImageTk.PhotoImage(resized)

root.geometry("1350x1300")

# Add image
label1=Label(root,image=bg)
label1.place(x=0,y=0,relwidth=1,relheight=1)

datetime_obj = datetime.now()
dte = datetime_obj.date()
present_file_path = f"C:/Users/cjaga/students/{dte}_present.csv"
absent_file_path = f"C:/Users/cjaga/students/{dte}_absent.csv"
image_path = "C:/Users/cjaga/Desktop/face recognition system/Photos/"


known_faces = ["jagan", "deekshith", "nithin"]
for i in known_faces:
	image = face_recognition.load_image_file(image_path + i + ".jpg")
	exec(f"{i}_encoding= face_recognition.face_encodings(image)[0]")
            
known_face_encoding = [jagan_encoding,deekshith_encoding, nithin_encoding]

known_faces_names = ["jagan", "deekshith", "nithin",]


def start_attendance():   
	video_capture = cv2.VideoCapture(0)
	print ("Starting video capture")
	students = known_faces_names.copy()
	##To create csv files
	# assign header columns
	pre_headerList = ['Name', 'Time']
	ab_headerList = ['Name']

	# open CSV file and assign header
	with open(present_file_path, 'w') as file1:
		dw1 = csv.DictWriter(file1, delimiter=',', fieldnames=pre_headerList)
		dw1.writeheader()
	with open(absent_file_path, 'w') as file2:
		dw2 = csv.DictWriter(file2, delimiter=',', fieldnames=ab_headerList)
		dw2.writeheader()

	file1.close()
	file2.close()

	face_locations = []
	face_encodings = []
	face_names = []
	s = True

	while True:
		_, frame = video_capture.read()
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)					
		rgb_small_frame = small_frame[:, :, ::-1]
		if s:
			face_locations = face_recognition.face_locations(rgb_small_frame)
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
			face_names = []
			for face_encoding in face_encodings:
				matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
				name = ""
				face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
				best_match_index = np.argmin(face_distance)
				if matches[best_match_index]:
					name = known_faces_names[best_match_index]

				face_names.append(name)
				if name in known_faces_names:
					font = cv2.FONT_HERSHEY_SIMPLEX
					bottomLeftCornerOfText = (10, 100)
					fontScale = 1.5
					fontColor = (255, 0, 0)
					thickness = 3
					lineType = 2

					cv2.putText(frame, name + ' Present',
					bottomLeftCornerOfText,
								font,
								fontScale,
								fontColor,
								thickness,
								lineType)
					if name in students:
						students.remove(name)
						#print(students)
						
						present_students = []
						for j in known_faces_names:
							if j not in students:
								present_students.append(j)

						now = datetime.now()
						current_time = now.strftime("%H:%M %p")

						#present students
						for x in present_students:
							with open(present_file_path, 'a') as file3:
								dw3 = csv.DictWriter(file3, delimiter=',', fieldnames=pre_headerList, lineterminator='\n')
								dw3.writerow({'Name': x, 'Time': current_time})

		cv2.imshow("attendence system", frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

    ##absent students
	for y in students:
		with open(absent_file_path, 'a') as file4:
			dw3 = csv.DictWriter(file4, delimiter=',', fieldnames=ab_headerList, lineterminator='\n')
			dw3.writerow({'Name': y})

	##Dropping duplicate rows
	df_state = pd.read_csv(present_file_path)
	Dup_Rows = df_state[df_state.duplicated()]
	DF_RM_DUP1 = df_state.drop_duplicates(keep='first')
	DF_RM_DUP1.to_csv(present_file_path, mode="w", index=False)

	video_capture.release()
	cv2.destroyAllWindows()
	#return students
	
def view_records():
	f = open("Heading.html", "w")
	file_pr = pd.read_csv(present_file_path)
	file_pr.to_html(f"C:/Users/cjaga/students/{dte}_present.html")
	file_ab = pd.read_csv(absent_file_path)
	file_ab.to_html(f"C:/Users/cjaga/students/{dte}_absent.html")
	message = """
	<html>
	<head>
	</head>
	<body>
	<center>
	<h1><b>Attendance System</h1>
	<a href="C:/Users/cjaga/students">Click to see Student record</a>
	</body>
	</html>
	"""
	f.write(message)
	f.close()
	webbrowser.open_new_tab("Heading.html")	

def email_alert(subject, body, to):
	msg = EmailMessage()
	msg.set_content(body)
	msg["subject"] = subject
	msg["to"] = to
	
	user = "cjagankumar2001@gmail.com"
	msg["from"] = user
	password = "vexqvdonfaqfzrbi"
	
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login(user, password)
	server.send_message(msg)
	server.quit()

def ab_email():	
	list2=[]
	df = pd.read_csv(absent_file_path)
	for m in df['Name']:
		list2.append(m)
	#print (list2)
	for x in set(list2):
		with open('email.csv', 'r') as file:
			reader = csv.DictReader(file, fieldnames=['Name', 'Email', 'Register no'])
			next(reader, None)
			for row in reader:
				if row['Name'] == x:
					print(f"Sending email to {row['Name']}")
					email_alert(f"Absent on {dte}", f"Dear {row['Name']} ({row['Register no']})\n,You are absent on {dte}", row['Email'])
	

def changeOnHover(button, colorOnHover, colorOnLeave):
    
	button.bind("<Enter>", func=lambda e: button.config(background=colorOnHover))
	button.bind("<Leave>", func=lambda e: button.config(background=colorOnLeave))


label2= Label(root,text="Face Recognition Attendance System",fg="black",bg="blue",width=30,font=("Times",30,"bold"))
label2.place(x=300,y=0)

# Create a button
button1 = Button(root, text="Start Attendance", command=start_attendance,fg="black",bg="blue",width=25,height=4,font=("Times",12,"bold"))
button1.place(x=210,y=350)



button2 = Button(root, text="View Records", command=view_records,fg="black",bg="blue",width=25,height=4,font=("Times",12,"bold"))
button2.place(x=550,y=350)



button3 = Button(root, text="Send Email to absentee", command=ab_email,fg="black",bg="blue",width=25,height=4,font=("Times",12,"bold"))
button3.place(x=900,y=350)
changeOnHover(button1, "blue", "light blue")
changeOnHover(button2, "blue", "light blue")
changeOnHover(button3, "blue", "light blue")

#Start the Tkinter event loop
root.mainloop()