import cv2
import numpy as np
import json
import os
from datetime import datetime
import qrcode
from PIL import Image
import random
import time

class BestiePayWithOpenCV:
    def __init__(self):
        self.users_data = {}
        self.products = {}
        self.transactions = []
        self.cashback_rate = 0.05
        self.current_user = None
        
        # Initialize OpenCV face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.load_data()
        
    def load_data(self):
        """Load existing user and product data"""
        if os.path.exists('bestie_users.json'):
            with open('bestie_users.json', 'r') as f:
                self.users_data = json.load(f)
        
        # Products with discounts
        self.products = {
            'P001': {'name': 'Organic Apples 🍎', 'price': 3.99, 'discount': 0.10},
            'P002': {'name': 'Fresh Bread 🥖', 'price': 2.49, 'discount': 0.05},
            'P003': {'name': 'Diamond Face Mask 💎', 'price': 15.99, 'discount': 0.20},
            'P004': {'name': 'Premium Coffee ☕', 'price': 8.99, 'discount': 0.15},
            'P005': {'name': 'Beauty Smoothie 🥤', 'price': 4.99, 'discount': 0.25}
        }

    def clear_screen(self):
        """Clear terminal"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def capture_face(self):
        """Capture face using OpenCV"""
        print("\n📸 Starting camera... Look at the camera bestie!")
        
        # Initialize camera
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("😅 Couldn't open camera! Using demo mode.")
            return None
        
        print("\n✨ Instructions:")
        print("   • Press 'SPACE' to capture your face")
        print("   • Press 'q' to quit\n")
        
        face_captured = None
        face_coords = None
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(frame, "BESTIE DETECTED! 💚", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                face_coords = (x, y, w, h)
            
            # Add instructions
            cv2.putText(frame, "SPACE: Capture | q: Quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('BestiePay Face Capture 💚', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(faces) > 0:
                # Capture the face
                x, y, w, h = faces[0]
                face_captured = gray[y:y+h, x:x+w]
                break
            elif key == ord('q'):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()
        
        if face_captured is not None:
            print("\n✨ Face captured successfully!")
            return face_captured
        else:
            print("\n😅 No face captured!")
            return None

    def register_user(self):
        """Register new user with face capture"""
        self.clear_screen()
        print("🌸" * 30)
        print("🌸     NEW BESTIE REGISTRATION     🌸")
        print("🌸" * 30)
        
        name = input("\n💚 Your name: ")
        email = input("💚 Your email: ")
        
        print("\n📸 Time to capture your beautiful face!")
        face_image = self.capture_face()
        
        if face_image is None:
            print("\n😅 Using demo mode without face data...")
            face_encoding = f"demo_face_{random.randint(1000, 9999)}"
        else:
            # Create simple face encoding (hash of the image)
            face_bytes = face_image.tobytes()
            face_encoding = hashlib.sha256(face_bytes).hexdigest()[:32]
        
        # Create user
        user_id = f"USER_{len(self.users_data) + 1:03d}"
        self.users_data[user_id] = {
            'name': name,
            'email': email,
            'face_encoding': face_encoding,
            'balance': 1000.00,
            'points': 0,
            'transactions': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\n" + "✨" * 30)
        print(f"✨ WELCOME {name.upper()}! ✨")
        print("✨" * 30)
        print(f"\n💚 Your Bestie ID: {user_id}")
        print(f"💰 Welcome balance: ${1000:.2f}")
        
        self.save_data()
        input("\n✨ Press Enter to continue...")

    def recognize_face(self):
        """Recognize user by face"""
        self.clear_screen()
        print("🔍" * 30)
        print("🔍     FACE RECOGNITION     🔍")
        print("🔍" * 30)
        
        print("\n📸 Looking for your face...")
        face_image = self.capture_face()
        
        if face_image is None:
            print("\n📱 Switching to manual login...")
            return self.manual_login()
        
        # Create encoding of captured face
        face_bytes = face_image.tobytes()
        current_encoding = hashlib.sha256(face_bytes).hexdigest()[:32]
        
        # Compare with stored faces
        for user_id, user_data in self.users_data.items():
            if user_data.get('face_encoding') == current_encoding:
                print(f"\n✨ Welcome back {user_data['name']}! ✨")
                self.current_user = user_data
                return user_id
        
        print("\n😅 Face not recognized! Try manual login.")
        return self.manual_login()

    def manual_login(self):
        """Manual login fallback"""
        print("\n🌸 Manual Login:")
        
        if not self.users_data:
            print("No users yet! Please register first.")
            return None
        
        users_list = list(self.users_data.items())
        for i, (user_id, user_data) in enumerate(users_list, 1):
            print(f"{i}. {user_data['name']} (${user_data['balance']:.2f})")
        
        try:
            choice = int(input("\n💚 Select user: ")) - 1
            if 0 <= choice < len(users_list):
                user_id, user_data = users_list[choice]
                self.current_user = user_data
                print(f"\n✨ Welcome back {user_data['name']}! ✨")
                return user_id
        except:
            pass
        
        return None

    def display_products(self):
        """Show products with discounts"""
        self.clear_screen()
        print("🛍️" * 30)
        print("🛍️     TODAY'S SPECIALS     🛍️")
        print("🛍️" * 30)
        
        for code, product in self.products.items():
            final_price = product['price'] * (1 - product['discount'])
            print(f"\n{code}: {product['name']}")
            print(f"   💲 Was: ${product['price']:.2f}")
            print(f"   🏷️  Discount: {product['discount']*100:.0f}% OFF!")
            print(f"   💚 NOW: ${final_price:.2f}")
            print("-" * 40)

    def make_payment(self, user_id, amount, method):
        """Process payment with cashback"""
        if user_id not in self.users_data:
            print("😅 User not found!")
            return False
        
        user = self.users_data[user_id]
        
        if user['balance'] < amount:
            print(f"😅 Insufficient funds! You have ${user['balance']:.2f}")
            return False
        
        # Process payment
        user['balance'] -= amount
        cashback = amount * self.cashback_rate
        user['balance'] += cashback
        points = int(amount * 10)
        user['points'] += points
        
        # Record transaction
        transaction = {
            'id': f"TXN_{len(self.transactions) + 1:04d}",
            'amount': amount,
            'cashback': cashback,
            'method': method,
            'points': points,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(transaction)
        user['transactions'].append(transaction)
        
        # Show success
        self.clear_screen()
        print("🎉" * 30)
        print("🎉   PAYMENT SUCCESSFUL!   🎉")
        print("🎉" * 30)
        print(f"\n💚 Amount: ${amount:.2f}")
        print(f"💰 Cashback: +${cashback:.2f}")
        print(f"⭐ Points: +{points}")
        print(f"\n💚 New balance: ${user['balance']:.2f}")
        
        input("\n✨ Press Enter to continue...")
        return True

    def generate_qr(self):
        """Generate QR code for payment"""
        self.clear_screen()
        print("📱" * 30)
        print("📱     QR CODE PAYMENT     📱")
        print("📱" * 30)
        
        amount = float(input("\n💚 Enter amount: $"))
        
        # Create QR code data
        qr_data = f"bestiepay://payment?amount={amount}&time={datetime.now().timestamp()}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save with timestamp
        filename = f"qr_bestie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        qr_image.save(filename)
        
        print(f"\n✅ QR Code saved: {filename}")
        
        try:
            qr_image.show()
        except:
            print("📁 Check your folder for the QR code!")
        
        input("\n✨ Press Enter after scanning...")
        return amount

    def view_profile(self, user_id):
        """View user profile"""
        if user_id not in self.users_data:
            return
        
        user = self.users_data[user_id]
        
        self.clear_screen()
        print("👤" * 30)
        print(f"👤     {user['name'].upper()}'S PROFILE     👤")
        print("👤" * 30)
        
        print(f"\n💚 Name: {user['name']}")
        print(f"📧 Email: {user['email']}")
        print(f"💰 Balance: ${user['balance']:.2f}")
        print(f"⭐ Points: {user['points']}")
        print(f"📅 Joined: {user['created_at']}")
        
        if user['transactions']:
            print("\n📋 Recent transactions:")
            for t in user['transactions'][-3:]:
                print(f"   • ${t['amount']:.2f} - {t['timestamp'][:10]}")
        
        input("\n✨ Press Enter to continue...")

    def main_menu(self):
        """Main menu"""
        self.clear_screen()
        print("""
    ╔═══════════════════════════════════════╗
    ║     💚  BESTIEPAY with OpenCV  💚    ║
    ║     Face Recognition Payment System   ║
    ║        5% Cashback Always! ✨         ║
    ╚═══════════════════════════════════════╝
        """)
        
        print("\n1. 🌸 Register New Bestie")
        print("2. 😊 Login with Face")
        print("3. 🚪 Exit")
        
        choice = input("\n💚 Choose: ")
        
        if choice == '1':
            self.register_user()
        elif choice == '2':
            user_id = self.recognize_face()
            if user_id:
                self.user_menu(user_id)
        elif choice == '3':
            self.save_data()
            print("\n💚 Bye bestie! 💚")
            return False
        
        return True

    def user_menu(self, user_id):
        """User menu after login"""
        while True:
            self.clear_screen()
            user = self.users_data[user_id]
            
            print(f"\n💚 Welcome back, {user['name']}! 💚")
            print(f"💰 Balance: ${user['balance']:.2f} | ⭐ Points: {user['points']}")
            print("\n" + "=" * 40)
            
            print("\n1. 🛍️  Shop Products")
            print("2. 💳 Make Payment")
            print("3. 📱 QR Code Payment")
            print("4. 👤 View Profile")
            print("5. 📋 Transaction History")
            print("6. 🚪 Logout")
            
            choice = input("\n💚 Choose: ")
            
            if choice == '1':
                self.display_products()
                code = input("\n💚 Enter product code: ").upper()
                if code in self.products:
                    product = self.products[code]
                    amount = product['price'] * (1 - product['discount'])
                    self.make_payment(user_id, amount, "Product")
                else:
                    print("😅 Invalid code!")
                    time.sleep(1)
            
            elif choice == '2':
                amount = float(input("\n💚 Amount: $"))
                self.make_payment(user_id, amount, "Manual")
            
            elif choice == '3':
                amount = self.generate_qr()
                self.make_payment(user_id, amount, "QR Code")
            
            elif choice == '4':
                self.view_profile(user_id)
            
            elif choice == '5':
                self.view_transactions(user_id)
            
            elif choice == '6':
                break

    def view_transactions(self, user_id):
        """View transaction history"""
        user = self.users_data[user_id]
        
        self.clear_screen()
        print("📋" * 30)
        print("📋     TRANSACTION HISTORY     📋")
        print("📋" * 30)
        
        if not user['transactions']:
            print("\n✨ No transactions yet!")
        else:
            for t in user['transactions'][-10:]:
                print(f"\n{t['timestamp']}")
                print(f"   💰 ${t['amount']:.2f}")
                print(f"   💚 Cashback: +${t['cashback']:.2f}")
                print(f"   ⭐ Points: +{t['points']}")
                print(f"   💳 {t['method']}")
        
        input("\n✨ Press Enter to continue...")

    def save_data(self):
        """Save data to file"""
        with open('bestie_users.json', 'w') as f:
            json.dump(self.users_data, f, indent=2)
        print("\n💾 Data saved bestie!")

def main():
    """Main function"""
    print("""
    📦 Installing required packages...
    
    Run these commands in terminal:
    
    1. brew install cmake
    2. pip install opencv-python
    3. pip install opencv-python-headless
    4. pip install numpy
    5. pip install pillow
    6. pip install qrcode[pil]
    
    Or just run this one command:
    pip install opencv-python opencv-python-headless numpy pillow qrcode[pil]
    """)
    
    input("✨ Press Enter to start BestiePay...")
    
    app = BestiePayWithOpenCV()
    
    while True:
        if not app.main_menu():
            break

if __name__ == "__main__":
    main()