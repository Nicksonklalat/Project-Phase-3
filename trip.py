import psycopg2

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "tripcar"
DB_USER = "postgres"
DB_PASSWORD = "pass"

def create_tables():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        id_no VARCHAR(50),
        phone_number VARCHAR(15)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trip_details (
        trip_id SERIAL PRIMARY KEY,
        start_location VARCHAR(100),
        end_location VARCHAR(100),
        trip_date DATE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id SERIAL PRIMARY KEY,
        total_passengers INTEGER,
        price DECIMAL,
        user_id INTEGER REFERENCES users(user_id),
        trip_id INTEGER REFERENCES trip_details(trip_id)
    );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def register_user(name, id_no, phone_number):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO users (name, id_no, phone_number) VALUES (%s, %s, %s) RETURNING user_id;
    """, (name, id_no, phone_number))
    
    user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return user_id

def add_trip(start_location, end_location, trip_date):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO trip_details (start_location, end_location, trip_date) VALUES (%s, %s, %s) RETURNING trip_id;
    """, (start_location, end_location, trip_date))
    
    trip_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return trip_id

def book_trip(user_id, trip_id, total_passengers):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    price = total_passengers * 40.0  # Changed price calculation to multiply by 40
    
    cursor.execute("""
    INSERT INTO bookings (total_passengers, price, user_id, trip_id) VALUES (%s, %s, %s, %s) RETURNING booking_id;
    """, (total_passengers, price, user_id, trip_id))
    
    booking_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return booking_id

def view_bookings(user_id):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT b.booking_id, b.total_passengers, b.price, td.start_location, td.end_location, td.trip_date
    FROM bookings b
    JOIN trip_details td ON b.trip_id = td.trip_id
    WHERE b.user_id = %s;
    """, (user_id,))
    
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return bookings

def view_booking_details(booking_id):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT b.booking_id, b.total_passengers, b.price, u.name, u.phone_number, 
           td.start_location, td.end_location, td.trip_date
    FROM bookings b
    JOIN users u ON b.user_id = u.user_id
    JOIN trip_details td ON b.trip_id = td.trip_id
    WHERE b.booking_id = %s;
    """, (booking_id,))
    
    booking_details = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return booking_details

def delete_booking(booking_id):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM bookings WHERE booking_id = %s;
    """, (booking_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    create_tables()
    
    print("Welcome to the Car Trip Booking System!")
    
    while True:
        print("\nMenu:")
        print("1. Register User")
        print("2. Add Trip")
        print("3. Book Trip")
        print("4. View Your Bookings")
        print("5. View Booking Details")
        print("6. Delete Booking")
        print("7. Exit")

        choice = input("Please choose an option (1-7): ")
        
        if choice == '1':
            name = input("Enter your name: ")
            id_no = input("Enter your ID number: ")
            phone_number = input("Enter your phone number: ")
            user_id = register_user(name, id_no, phone_number)
            print(f"Registration successful! Your User ID is: {user_id}")
        
        elif choice == '2':
            print("Please enter trip details:")
            start_location = input("Start Location: ")
            end_location = input("End Location: ")
            trip_date = input("Trip Date (YYYY-MM-DD): ")
            trip_id = add_trip(start_location, end_location, trip_date)
            print(f"Trip added successfully! Trip ID is: {trip_id}")
        
        elif choice == '3':
            user_id = int(input("Enter your User ID: "))
            total_passengers = int(input("Enter the number of passengers: "))
            trip_id = int(input("Enter the Trip ID: "))
            booking_id = book_trip(user_id, trip_id, total_passengers)
            print(f"Booking successful! Your Booking ID is: {booking_id}")

        elif choice == '4':
            user_id = int(input("Enter your User ID to view your bookings: "))
            bookings = view_bookings(user_id)
            if bookings:
                print("Your Bookings:")
                for booking in bookings:
                    print(f"Booking ID: {booking[0]}, Passengers: {booking[1]}, Price: ${booking[2]}, Trip: {booking[3]} to {booking[4]}, Date: {booking[5]}")
            else:
                print("No bookings found for this user.")
        
        elif choice == '5':
            booking_id = int(input("Enter the Booking ID to view details: "))
            details = view_booking_details(booking_id)
            if details:
                print(f"Booking ID: {details[0]}")
                print(f"Total Passengers: {details[1]}")
                print(f"Price: ${details[2]}")
                print(f"User Name: {details[3]}")
                print(f"User Phone Number: {details[4]}")
                print(f"Trip Start Location: {details[5]}")
                print(f"Trip End Location: {details[6]}")
                print(f"Trip Date: {details[7]}")
            else:
                print("Booking not found.")
        
        elif choice == '6':
            booking_id = int(input("Enter the Booking ID to delete: "))
            delete_booking(booking_id)
            print(f"Booking ID {booking_id} deleted successfully.")

        elif choice == '7':
            print("Thank you for using the Car Trip Booking System. WELCOME!")
            break
        
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
