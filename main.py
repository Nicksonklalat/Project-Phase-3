import psycopg2

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "dbname": "tripcar",
    "user": "postgres",
    "password": "pass"
}

def create_tables():
    """Creates necessary tables in the database if they do not exist."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        id_no VARCHAR(50),
        phone_number VARCHAR(15)
    );
    """)
    
    # Create trip_details table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trip_details (
        trip_id SERIAL PRIMARY KEY,
        start_location VARCHAR(100),
        end_location VARCHAR(100),
        trip_date DATE
    );
    """)
    
    # Create bookings table
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

def register_user(user_info):
    """Registers a new user in the database and returns the user ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Insert user information into the users table
    cursor.execute("""
    INSERT INTO users (name, id_no, phone_number) VALUES (%s, %s, %s) RETURNING user_id;
    """, (user_info["name"], user_info["id_no"], user_info["phone_number"]))
    
    user_id = cursor.fetchone()[0]  # Get the newly created user ID
    conn.commit()  
    cursor.close()  
    conn.close()  
    
    return user_id

def add_trip(trip_info):
    """Adds a new trip to the database and returns the trip ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Insert trip information into the trip_details table
    cursor.execute("""
    INSERT INTO trip_details (start_location, end_location, trip_date) VALUES (%s, %s, %s) RETURNING trip_id;
    """, (trip_info["start_location"], trip_info["end_location"], trip_info["trip_date"]))
    
    trip_id = cursor.fetchone()[0]  # Get the newly created trip ID
    conn.commit()  
    cursor.close()  
    conn.close()  
    
    return trip_id

def book_trip(user_id, trip_id, total_passengers):
    """Books a trip for a user and returns the booking ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Calculate price based on the number of passengers
    price = total_passengers * 40.0
    
    # Insert booking information into the bookings table
    cursor.execute("""
    INSERT INTO bookings (total_passengers, price, user_id, trip_id) VALUES (%s, %s, %s, %s) RETURNING booking_id;
    """, (total_passengers, price, user_id, trip_id))
    
    booking_id = cursor.fetchone()[0]  
    conn.commit()  
    cursor.close()  
    conn.close()  
    
    return booking_id

def view_bookings(user_id):
    """Retrieves all bookings for a given user ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Query to get bookings associated with the user
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
    """Retrieves detailed information for a specific booking ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Query to get detailed booking information
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
    """Deletes a booking from the database using the booking ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Delete booking record
    cursor.execute("""
    DELETE FROM bookings WHERE booking_id = %s;
    """, (booking_id,))
    
    conn.commit()  
    cursor.close()  
    conn.close()  
def update_user(user_id, user_info):
    """Updates user information in the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Update user record with new information
    cursor.execute("""
    UPDATE users SET name = %s, id_no = %s, phone_number = %s WHERE user_id = %s;
    """, (user_info["name"], user_info["id_no"], user_info["phone_number"], user_id))
    
    conn.commit()  
    cursor.close()  
    conn.close()  

def update_trip(trip_id, trip_info):
    """Updates trip details in the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Update trip record with new information
    cursor.execute("""
    UPDATE trip_details SET start_location = %s, end_location = %s, trip_date = %s WHERE trip_id = %s;
    """, (trip_info["start_location"], trip_info["end_location"], trip_info["trip_date"], trip_id))
    
    conn.commit()  
    cursor.close()  
    conn.close()  

def update_booking(booking_id, total_passengers):
    """Updates booking details in the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Calculate new price based on updated number of passengers
    price = total_passengers * 40.0
    
    # Update booking record with new passenger count and price
    cursor.execute("""
    UPDATE bookings SET total_passengers = %s, price = %s WHERE booking_id = %s;
    """, (total_passengers, price, booking_id))
    
    conn.commit() 
    cursor.close()  
    conn.close()  

def main():
    """Main function to run the Car Trip Booking system."""
    create_tables()  
    
    print("Welcome to the Car Trip Booking!")
    
    while True:
        # Display the menu options
        print("\nMenu:")
        print("1. Register User")
        print("2. Add Trip")
        print("3. Book Trip")
        print("4. View Your Bookings")
        print("5. View Booking Details")
        print("6. Delete Booking")
        print("7. Update User Information")
        print("8. Update Trip Details")
        print("9. Update Booking")
        print("10. Exit")

        choice = input("Please choose an option (1-10): ")
        
        # User registration
        if choice == '1':
            user_info = {
                "name": input("Enter your name: "),
                "id_no": input("Enter your ID number: "),
                "phone_number": input("Enter your phone number: ")
            }
            user_id = register_user(user_info)
            print(f"Registration successful! Your User ID is: {user_id}")
        
        # Add a new trip
        elif choice == '2':
            trip_info = {
                "start_location": input("Start Location: "),
                "end_location": input("End Location: "),
                "trip_date": input("Trip Date (YYYY-MM-DD): ")
            }
            trip_id = add_trip(trip_info)
            print(f"Trip added successfully! Trip ID is: {trip_id}")
        
        # Book a trip
        elif choice == '3':
            user_id = int(input("Enter your User ID: "))
            total_passengers = int(input("Enter the number of passengers: "))
            trip_id = int(input("Enter the Trip ID: "))
            booking_id = book_trip(user_id, trip_id, total_passengers)
            print(f"Booking successful! Your Booking ID is: {booking_id}")

        # View user's bookings
        elif choice == '4':
            user_id = int(input("Enter your User ID to view your bookings: "))
            bookings = view_bookings(user_id)
            if bookings:
                print("Your Bookings:")
                for booking in bookings:
                    print(f"Booking ID: {booking[0]}, Passengers: {booking[1]}, Price: ${booking[2]}, Trip: {booking[3]} to {booking[4]}, Date: {booking[5]}")
            else:
                print("No bookings found for this user.")
        
        # View details of a specific booking
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
        
        # Delete a specific booking
        elif choice == '6':
            booking_id = int(input("Enter the Booking ID to delete: "))
            delete_booking(booking_id)
            print(f"Booking ID {booking_id} deleted successfully.")

        # Update user information
        elif choice == '7':
            user_id = int(input("Enter your User ID to update: "))
            user_info = {
                "name": input("Enter new name: "),
                "id_no": input("Enter new ID number: "),
                "phone_number": input("Enter new phone number: ")
            }
            update_user(user_id, user_info)
            print("User information updated successfully.")

        # Update trip details
        elif choice == '8':
            trip_id = int(input("Enter the Trip ID to update: "))
            trip_info = {
                "start_location": input("New Start Location: "),
                "end_location": input("New End Location: "),
                "trip_date": input("New Trip Date (YYYY-MM-DD): ")
            }
            update_trip(trip_id, trip_info)
            print("Trip details updated successfully.")

        # Update booking details
        elif choice == '9':
            booking_id = int(input("Enter the Booking ID to update: "))
            total_passengers = int(input("Enter the new number of passengers: "))
            update_booking(booking_id, total_passengers)
            print("Booking updated successfully.")

        # Exit the program
        elif choice == '10':
            print("Thank you for using the Car Trip Booking. WELCOME!")
            break
        
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()  # Run the main function
