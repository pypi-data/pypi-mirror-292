import os
import time
import threading
from typing import Optional, Tuple, Any, Callable
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, DictLoader, select_autoescape
from cryptography.fernet import Fernet, InvalidToken
import base64
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http import cookies

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=True)  # New column for last name
    EmailAddress = Column(String, nullable=False, unique=True)
    AuthorizedFlag = Column(Boolean, default=False)  # New column for authorization
    AdminFlag = Column(Boolean, default=False)  # New column for admin status

class Code(Base):
    __tablename__ = 'codes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)

class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)
    image_directory = Column(String, nullable=True)  # Optional field for image directory path
    title = Column(String, nullable=True)  # Optional field for thread title

class OTCAuthSystem:
    def __init__(self,
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 login_link_base_url: Optional[str] = None,
                 reply_to_addr: Optional[str] = None,
                 fernet_key: Optional[str] = None,
                 expiration_time: Optional[int] = None,
                 db_path: Optional[str] = None,
                 email_template: Optional[str] = None,
                 smtp_factory: Optional[Callable[[], Any]] = None,
                 root_user_email: Optional[str] = None):
        # Load environment variables from the main project's .env file
        load_dotenv()
        
        # SMTP configuration
        self.smtp_server: str = smtp_server or os.getenv("SMTP_SERVER")
        self.smtp_port: int = smtp_port or int(os.getenv("SMTP_PORT", 587))  # default to 587 if not provided
        self.smtp_username: str = smtp_username or os.getenv("SMTP_USERNAME")
        self.smtp_password: str = smtp_password or os.getenv("SMTP_PASSWORD")
        self.login_link_base_url: str = login_link_base_url or os.getenv("LOGIN_LINK_BASE_URL")

        # Optional Reply-To address
        self.reply_to_addr: Optional[str] = reply_to_addr or os.getenv("REPLY_TO_ADDR")

        # Encryption key for Fernet
        key: str = fernet_key or os.getenv("FERNET_KEY")
        if not key:
            raise ValueError("FERNET_KEY environment variable is required")
        self.fernet: Fernet = Fernet(base64.urlsafe_b64encode(key.encode()))

        # Expiration time for codes in seconds (e.g., 600 seconds = 10 minutes)
        self.expiration_time: int = expiration_time or int(os.getenv("EXPIRATION_TIME", 600))

        # Database configuration
        self.db_path: str = db_path or os.getenv("DB_PATH", "users.db")
        self.engine = create_engine(f'sqlite:///{self.db_path}', pool_size=10, max_overflow=20, echo=False)
        
        # Ensure the database and tables are created
        self._initialize_database()

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        # Email template configuration
        self.email_template: Optional[str] = email_template

        # Factory for creating SMTP client (can be mocked in tests)
        self.smtp_factory = smtp_factory or self._default_smtp_factory

        # Root user email, using the provided parameter or fallback to .env value
        self.root_user_email = root_user_email or os.getenv("ROOT_USER")

        # Check if the "users" table is empty and add the root user if necessary
        self._add_root_user_if_empty()

        # Start the background thread for cleaning up expired codes
        self.cleanup_interval: int = 6 * 3600  # 6 hours in seconds
        self._start_cleanup_thread()

    def _initialize_database(self) -> None:
        """Create the SQLite database and the necessary tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def _start_cleanup_thread(self) -> None:
        """Start a background thread to remove expired codes every cleanup_interval seconds."""
        def run_cleanup() -> None:
            while True:
                time.sleep(self.cleanup_interval)
                self._remove_expired_codes()

        thread = threading.Thread(target=run_cleanup, daemon=True)
        thread.start()

    def _store_code_in_db(self, code: str, email: str, timestamp: float) -> None:
        """Store the code, email, and timestamp in the SQLite database."""
        session = self.Session()
        try:
            new_code = Code(code=code, email=email, timestamp=timestamp)
            session.add(new_code)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during code storage: {e}")
        finally:
            session.close()

    def _get_code_from_db(self, code: str) -> Optional[Code]:
        """Retrieve a code entry from the database."""
        session = self.Session()
        try:
            return session.query(Code).filter(Code.code == code).one_or_none()
        except SQLAlchemyError as e:
            print(f"Database error during code retrieval: {e}")
            return None
        finally:
            session.close()

    def _delete_code_from_db(self, code: str) -> None:
        """Delete a code entry from the database."""
        session = self.Session()
        try:
            code_entry = session.query(Code).filter(Code.code == code).one_or_none()
            if code_entry:
                session.delete(code_entry)
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during code deletion: {e}")
        finally:
            session.close()

    def _remove_expired_codes(self) -> None:
        """Remove expired codes from the database."""
        session = self.Session()
        current_time = time.time()
        try:
            expired_codes = session.query(Code).filter(current_time - Code.timestamp > self.expiration_time).all()
            for code_entry in expired_codes:
                session.delete(code_entry)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during expired code cleanup: {e}")
        finally:
            session.close()

    def _default_smtp_factory(self):
        """Creates and returns a default SMTP client using the provided configuration."""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(self.smtp_username, self.smtp_password)
            return server
        except smtplib.SMTPException as e:
            print(f"Failed to create SMTP client: {e}")
            raise

    def _add_root_user_if_empty(self):
        """Check if the users table is empty, and add the root user if it is."""
        session = self.Session()
        try:
            user_count = session.query(User).count()
            if user_count == 0:
                if self.root_user_email:
                    root_user = User(
                        FirstName="Root",
                        LastName="User",
                        EmailAddress=self.root_user_email,
                        AuthorizedFlag=True,
                        AdminFlag=True
                    )
                    session.add(root_user)
                    session.commit()
                    print("Root user added successfully.")
                else:
                    print("Root user email is not provided. Root user not added.")
            else:
                print("Users table is not empty. No root user added.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during root user addition: {e}")
        finally:
            session.close()

    def get_user_info(self, email: str) -> Optional[Tuple[str, str]]:
        """Retrieve user information from the database by email."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.EmailAddress == email).one()
            return user.FirstName, user.EmailAddress
        except NoResultFound:
            return None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def generate_code(self, email: str) -> str:
        """Encrypt the email address and timestamp to generate a one-time code."""
        timestamp = time.time()
        data = f"{email}|{timestamp}"
        encrypted_data = self.fernet.encrypt(data.encode()).decode()
        self._store_code_in_db(encrypted_data, email, timestamp)
        return encrypted_data

    def send_login_email(self, email: str, code: str, first_name: str) -> None:
        """Send a login email with a one-time link."""
        login_link = f"{self.login_link_base_url}/{code}"

        # Setup Jinja2 environment
        if self.email_template:
            # Use the provided email template string
            env = Environment(
                loader=DictLoader({'otc_email.html': self.email_template}),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            # Load templates from the 'templates' folder
            env = Environment(
                loader=FileSystemLoader(os.path.join(os.getcwd(), 'templates')),
                autoescape=select_autoescape(['html', 'xml'])
            )

        # Load and render the template
        template = env.get_template('otc_email.html')
        html_content = template.render(login_link=login_link, first_name=first_name)

        # Create the email message
        msg = MIMEMultipart()
        msg["Subject"] = "Your Login Link"
        msg["From"] = self.smtp_username
        msg["To"] = email

        # Set the Reply-To address if provided
        if self.reply_to_addr:
            msg.add_header('Reply-To', self.reply_to_addr)

        # Attach the HTML content
        msg.attach(MIMEText(html_content, "html"))

        # Send the email
        with self.smtp_factory() as server:
            server.send_message(msg)

    def generate_and_send_email(self, email: str) -> Optional[str]:
        """Generate a one-time code, send it via email, and store it, if the email exists in the database."""
        user_info = self.get_user_info(email)
        if user_info:
            first_name, email_address = user_info
            code = self.generate_code(email_address)
            self.send_login_email(email_address, code, first_name)
            return code
        else:
            print("Email not found in the database.")
            return None

    def validate_code_and_generate_cookie(self, code: str) -> Optional[Tuple[str, str]]:
        """Validate the given code, generate httpOnly cookie if valid, and return cookie string and email."""
        code_entry = self._get_code_from_db(code)
        print(code)
        print(code_entry)
        if code_entry:
            current_time = time.time()
            if current_time - code_entry.timestamp > self.expiration_time:
                print("Code has expired.")
                self._delete_code_from_db(code)
                return None
            
            # If the code is valid, generate the httpOnly cookie
            email = code_entry.email
            cookie = cookies.SimpleCookie()
            token = self.fernet.encrypt(email.encode()).decode()
            cookie['auth_token'] = token
            cookie['auth_token']['httponly'] = True
            cookie['auth_token']['path'] = '/'  # Set cookie path
            cookie['auth_token']['max-age'] = os.getenv("COOKIE_LIFE")  # 12 hours in seconds

            # Return the httpOnly cookie string and email
            return cookie['auth_token'].OutputString(), email

        print("Invalid or expired code.")
        return None
    
    def validate_http_only_cookie(self, cookie_value: str) -> Optional[str]:
        """Validate the httpOnly cookie."""
        try:
            email = self.fernet.decrypt(cookie_value.encode()).decode()
            return email
        except InvalidToken:
            print("Invalid or expired cookie.")
            return None

    def purge_valid_codes(self) -> None:
        """Purge all valid codes from the database."""
        session = self.Session()
        try:
            session.query(Code).delete()
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during code purge: {e}")
        finally:
            session.close()

    def get_all_users(self) -> Optional[list]:
        """Retrieve all users from the database, ordered by ID in descending order."""
        session = self.Session()
        try:
            users = session.query(User).order_by(User.id.desc()).all()
            return users
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def edit_user(self, user_id: int, **kwargs) -> bool:
        """Edit one or more columns in a user object."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                print("User not found.")
                return False
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during user edit: {e}")
            return False
        finally:
            session.close()

    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database by user ID."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                print("User not found.")
                return False
            session.delete(user)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during user deletion: {e}")
            return False
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a specific user from the database by email."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.EmailAddress == email).one_or_none()
            return user
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def add_user(self, first_name: str, last_name: Optional[str], email_address: str, authorized_flag: bool = False, admin_flag: bool = False) -> Optional[User]:
        """Add a new user to the database and return the user object, including the new ID."""
        session = self.Session()
        try:
            # Check if the email address already exists in the database
            existing_user = session.query(User).filter(User.EmailAddress == email_address).one_or_none()
            if existing_user:
                print(f"User with email {email_address} already exists.")
                return None

            # Create a new user object
            new_user = User(
                FirstName=first_name,
                LastName=last_name,
                EmailAddress=email_address,
                AuthorizedFlag=authorized_flag,
                AdminFlag=admin_flag
            )

            # Add the new user to the session and commit
            session.add(new_user)
            session.commit()

            # Refresh the session to retrieve the ID and return the user
            session.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during user addition: {e}")
            return None
        finally:
            session.close()

    def add_thread(self, thread_id: str, email: str, image_directory: Optional[str] = None, title: Optional[str] = None) -> None:
        """Add a new thread to the database, calculating the timestamp when the function is called."""
        session = self.Session()
        try:
            timestamp = time.time()  # Calculate the current timestamp
            new_thread = Thread(
                thread_id=thread_id,
                email=email,
                timestamp=timestamp,
                image_directory=image_directory,
                title=title
            )
            session.add(new_thread)
            session.commit()
            print(f"Thread {thread_id} added successfully.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during thread addition: {e}")
        finally:
            session.close()
    
    def get_threads_by_email(self, email: str) -> Optional[list]:
        """Retrieve all threads associated with a specific email."""
        session = self.Session()
        try:
            threads = session.query(Thread).filter(Thread.email == email).all()
            return threads
        except SQLAlchemyError as e:
            print(f"Database error during thread retrieval: {e}")
            return None
        finally:
            session.close()

    def delete_thread(self, thread_id: str) -> None:
        """Delete a thread from the database based on the thread ID."""
        session = self.Session()
        try:
            thread_entry = session.query(Thread).filter(Thread.thread_id == thread_id).one_or_none()
            if thread_entry:
                session.delete(thread_entry)
                session.commit()
                print(f"Thread {thread_id} deleted successfully.")
            else:
                print(f"Thread with ID {thread_id} not found.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during thread deletion: {e}")
        finally:
            session.close()


    def update_thread_image_url(self, thread_id: str, image_url: str) -> bool:
        """Update the image_directory field of a thread with a given thread_id."""
        session = self.Session()
        try:
            # Find the thread with the specified thread_id
            thread = session.query(Thread).filter(Thread.thread_id == thread_id).one_or_none()
            
            if not thread:
                print(f"Thread with ID {thread_id} not found.")
                return False
            
            # Update the image_directory with the new image_url
            thread.image_directory = image_url
            session.commit()
            print(f"Thread {thread_id} updated with new image URL: {image_url}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during thread update: {e}")
            return False
        finally:
            session.close()

    def update_thread_title(self, thread_id: str, title: str) -> bool:
        """Update the title field of a thread with a given thread_id."""
        session = self.Session()
        try:
            # Find the thread with the specified thread_id
            thread = session.query(Thread).filter(Thread.thread_id == thread_id).one_or_none()
            
            if not thread:
                print(f"Thread with ID {thread_id} not found.")
                return False
            
            # Update the title with the new title value
            thread.title = title
            session.commit()
            print(f"Thread {thread_id} updated with new title: {title}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during thread title update: {e}")
            return False
        finally:
            session.close()