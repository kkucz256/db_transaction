import random
import mysql.connector
from tkinter import *

pswrd = input("Enter your password: ")
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=pswrd,
    database="sakila"
)
cursor = conn.cursor()
cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")
existing_booking = None


def window_one():
    window = Tk()
    window.title("Client 2")
    window.geometry("400x300")

    seat_lbl = Label(window, text="Enter seat number:")
    seat_lbl.grid(row=0, column=0, padx=10, pady=10)
    seat_entry = Entry(window, width=10)
    seat_entry.grid(row=0, column=1, padx=10, pady=10)

    show_lbl = Label(window, text="Enter show number:")
    show_lbl.grid(row=1, column=0, padx=10, pady=10)
    show_entry = Entry(window, width=10)
    show_entry.grid(row=1, column=1, padx=10, pady=10)

    ticket_lbl = Label(window, text="Printed records go here")
    ticket_lbl.grid(row=4, column=0, columnspan=4, padx=10, pady=10)

    text_lbl = Label(window, text="Insert the seat and show above")
    text_lbl.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

    commit_btn = Button(window, text="Commit", width=8, command=lambda: commit_fun(text_lbl, seat_entry, show_entry))
    commit_btn.grid(row=1, column=3, padx=10, pady=10)

    print_btn = Button(window, text="Print last", width=8, command=lambda: print_ticket(ticket_lbl))
    print_btn.grid(row=0, column=2, padx=10, pady=10)

    book_btn = Button(window, text="Book", width=8, command=lambda: create_ticket(text_lbl, seat_entry, show_entry))
    book_btn.grid(row=1, column=2, padx=10, pady=10)

    close_btn = Button(window, text="Close", width=8, command=lambda: close_fun(window))
    close_btn.grid(row=0, column=3, padx=10, pady=10)
    window.mainloop()


def create_booking():
    cursor.execute("START TRANSACTION;")
    customer_id = random.randint(1, 600)
    payment_id = random.randint(1, 16000)
    cursor.execute(f"INSERT INTO booking (customer_id, payment_id) VALUES ({customer_id},{payment_id})")
    booking_id = cursor.lastrowid
    return booking_id


def create_ticket(label, seat_entry, show_entry):
    seat_id = seat_entry.get()
    show_id = show_entry.get()
    if seat_id == "" or show_id == "":
        label.config(text="You didn't provide seat id and/or show id!")
    elif int(seat_id) > 1000 or int(show_id) > 100:
        label.config(text="Seat and/or show with such id does not exist.")
    elif not check_show(int(show_id), int(seat_id)):
        label.config(text=f"There is no seat {seat_id} for show {show_id}.")
    else:
        global existing_booking
        cursor.execute(
            f"SELECT * FROM ticket WHERE seat_id = {int(seat_id)} AND show_id = {int(show_id)} AND taken ='BOOKED' FOR UPDATE;")
        existing_booking = cursor.fetchone()
        # print(existing_booking)

        if existing_booking:
            label.config(text="Seat is already booked. Cannot create a new booking.")
            cursor.nextset()
            cursor.execute("ROLLBACK;")
            return
        elif existing_booking is None:
            booking_id = create_booking()
            price = 25.50
            info = "BOOKED"
            label.config(text=f"Booked a seat {seat_id} for show {show_id}, waiting for commit.")

            cursor.execute(f"INSERT INTO ticket (seat_id, booking_id, show_id, price, taken) "
                           f"VALUES ({seat_id}, {booking_id}, {show_id}, {price}, '{info}');")


def commit_fun(label, seat_entry, show_entry):
    seat_id = seat_entry.get()
    show_id = show_entry.get()
    if seat_id == "" or show_id == "":
        label.config(text=f"Can't commit if the seat/show does not exist.")
    elif int(seat_id) > 1000 or int(show_id) > 100:
        label.config(text="There is no such show/seat so you can't commit.")
    elif existing_booking is None:
        label.config(text=f"Success! You booked seat no: {seat_id} for show {show_id}.")
    else:
        label.config(text=f"Can't commit if the seat {seat_id} is already booked.")
    conn.commit()


def close_fun(window):
    cursor.close()
    conn.close()
    window.destroy()


def print_ticket(label):
    cursor.execute("SELECT * FROM ticket ORDER BY booking_id DESC LIMIT 5;")
    ticket_data = cursor.fetchall()
    ticket_data_str = "\n".join([str(row) for row in ticket_data])
    label.config(text=ticket_data_str)


def check_show(show_id, seat_id):
    lower_show_range = 1
    upper_show_range = 10
    lower_seat_range = 1
    upper_seat_range = 100
    for i in range(1, 11):
        if show_id in range(lower_show_range, upper_show_range + 1):
            if seat_id in range(lower_seat_range, upper_seat_range + 1):
                return True
            else:
                return False
        else:
            lower_show_range += 10
            upper_show_range += 10
            lower_seat_range += 100
            upper_seat_range += 100

    return False


if __name__ == "__main__":
    window_one()
