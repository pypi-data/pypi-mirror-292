import nmap
from cryptography.fernet import Fernet as CryptographyFernet
import hashlib
import logging
import yara
import itertools
import socket
import requests
import subprocess
from scapy.all import sniff, IP
    
class NmapNetwork:
    """Class for network scanning using Nmap."""
    
    def __init__(self):
        pass

    @staticmethod
    def scan_network(ip):
        """
        Scans a network for open ports and services on a given IP address.
        
        Args:
            ip (str): The IP address to scan.
            
        Summary:
            Uses Nmap to scan the given IP address for open ports and displays
            the protocol and state of each port.
        """
        nm = nmap.PortScanner()
        nm.scan(ip, '1-1024')
        for host in nm.all_hosts():
            print(f'Host: {host} ({nm[host].hostname()})')
            for proto in nm[host].all_protocols():
                print(f'Protocol: {proto}')
                lport = nm[host][proto].keys()
                for port in lport:
                    print(f'Port: {port}\tState: {nm[host][proto][port]["state"]}')
            
class Fernet:
    """Class for encryption and decryption using Fernet symmetric encryption."""

    def __init__(self):
        pass

    @staticmethod
    def generate_key():
        """
        Generates a new Fernet key.
        
        Returns:
            bytes: The generated key.
            
        Summary:
            Generates and returns a new key for Fernet encryption.
        """
        return CryptographyFernet.generate_key()

    @staticmethod
    def encrypt_message(key, message):
        """
        Encrypts a message using the provided Fernet key.
        
        Args:
            key (bytes): The Fernet key.
            message (str): The message to encrypt.
            
        Returns:
            bytes: The encrypted message.
            
        Summary:
            Encrypts a given message using the specified Fernet key and returns
            the encrypted message.
        """
        f = CryptographyFernet(key)
        return f.encrypt(message.encode())

    @staticmethod
    def decrypt_message(key, encrypted_message):
        """
        Decrypts an encrypted message using the provided Fernet key.
        
        Args:
            key (bytes): The Fernet key.
            encrypted_message (bytes): The message to decrypt.
            
        Returns:
            str: The decrypted message.
            
        Summary:
            Decrypts a given encrypted message using the specified Fernet key and returns
            the decrypted message.
        """
        f = CryptographyFernet(key)
        return f.decrypt(encrypted_message).decode()

class HashLib:
    """Class for password hashing and verification using SHA-256."""
    
    def __init__(self):
        pass

    @staticmethod
    def hash_password(password):
        """
        Hashes a password using SHA-256.
        
        Args:
            password (str): The password to hash.
            
        Returns:
            str: The hashed password.
            
        Summary:
            Hashes a given password using SHA-256 and returns the hashed password.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(stored_password, provided_password):
        """
        Verifies a password against the stored hashed password.
        
        Args:
            stored_password (str): The stored hashed password.
            provided_password (str): The password to verify.
            
        Returns:
            bool: True if the password matches, False otherwise.
            
        Summary:
            Verifies a provided password by hashing it with SHA-256 and comparing
            it to the stored hashed password.
        """
        return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()
    
class Logging:
    """Class for setting up a logger to create and manage log files."""
    
    def __init__(self):
        pass

    @staticmethod
    def setup_logger(log_file):
        """
        Sets up a logger to log messages to a specified log file.
        
        Args:
            log_file (str): The path to the log file.
            
        Returns:
            logging.Logger: The configured logger.
            
        Summary:
            Configures and returns a logger that logs messages to the specified log file.
        """
        logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        return logger
    
class Yara:
    """Class for scanning files using Yara rules."""
    
    def __init__(self):
        pass

    @staticmethod
    def scan_file(rule_path, file_path):
        """
        Scans a file for matches against Yara rules.
        
        Args:
            rule_path (str): The path to the Yara rule file.
            file_path (str): The path to the file to scan.
            
        Returns:
            list: A list of matches found in the file.
            
        Summary:
            Compiles Yara rules from the specified rule file and scans the given file
            for matches, returning a list of found matches.
        """
        rules = yara.compile(filepath=rule_path)
        matches = rules.match(file_path)
        return matches

class BruteForce:
    """Class for performing brute force attacks to crack passwords."""
    
    def __init__(self):
        pass

    @staticmethod
    def brute_force_crack(password_set, target_password):
        """
        Attempts to crack a password using brute force.
        
        Args:
            password_set (str): The set of characters to use for brute force.
            target_password (str): The password to crack.
        
        Returns:
            str: The cracked password if found, else None.
        
        Summary:
            Uses brute force to attempt cracking the target password by generating
            all possible combinations from the provided character set.
        """
        for length in range(1, 6):
            for guess in itertools.product(password_set, repeat=length):
                guess = ''.join(guess)
                if guess == target_password:
                    return guess
        return None

class PortScanner:
    """Class for scanning open ports on a host."""
    
    def __init__(self):
        pass

    @staticmethod
    def scan_ports(host, start_port, end_port):
        """
        Scans open ports on a given host.
        
        Args:
            host (str): The host to scan.
            start_port (int): The starting port number.
            end_port (int): The ending port number.
        
        Returns:
            list: List of open ports.
        
        Summary:
            Scans the specified range of ports on the given host and returns a list
            of open ports.
        """
        open_ports = []
        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return open_ports

class SQLInjectionTester:
    """Class for testing SQL injection vulnerabilities."""
    
    def __init__(self):
        pass

    @staticmethod
    def test_sql_injection(url, payload):
        """
        Tests for SQL injection vulnerability.
        
        Args:
            url (str): The URL to test.
            payload (str): The SQL payload to use.
        
        Returns:
            bool: True if vulnerable, else False.
        
        Summary:
            Tests the given URL for SQL injection vulnerability using the provided
            SQL payload and returns whether the site is vulnerable.
        """
        response = requests.get(url + payload)
        return "syntax error" in response.text or "SQL" in response.text

class XSSTester:
    """Class for testing cross-site scripting (XSS) vulnerabilities."""
    
    def __init__(self):
        pass

    @staticmethod
    def test_xss(url, payload):
        """
        Tests for XSS vulnerability.
        
        Args:
            url (str): The URL to test.
            payload (str): The XSS payload to use.
        
        Returns:
            bool: True if vulnerable, else False.
        
        Summary:
            Tests the given URL for XSS vulnerability using the provided payload
            and returns whether the site is vulnerable.
        """
        response = requests.get(url, params={'q': payload})
        return payload in response.text

class CSRFTTester:
    """Class for testing cross-site request forgery (CSRF) vulnerabilities."""
    
    def __init__(self):
        pass

    @staticmethod
    def test_csrf(url, csrf_token, session):
        """
        Tests for CSRF vulnerability.
        
        Args:
            url (str): The URL to test.
            csrf_token (str): The CSRF token.
            session (requests.Session): The session object.
        
        Returns:
            bool: True if vulnerable, else False.
        
        Summary:
            Tests the given URL for CSRF vulnerability using the provided CSRF token
            and session object, and returns whether the site is vulnerable.
        """
        payload = {'csrf_token': csrf_token, 'action': 'test'}
        response = session.post(url, data=payload)
        return response.status_code == 200 and "CSRF" not in response.text

class TrafficSniffer:
    """Class for sniffing network traffic."""
    
    def __init__(self):
        pass

    @staticmethod
    def sniff_packets(interface, packet_count):
        """
        Sniffs network packets on a given interface.
        
        Args:
            interface (str): The network interface to sniff on.
            packet_count (int): The number of packets to capture.
        
        Returns:
            list: List of captured packets.
        
        Summary:
            Sniffs the specified number of packets on the given network interface
            and returns the captured packets.
        """
        return sniff(iface=interface, count=packet_count, filter="ip")

class PasswordStrengthChecker:
    """Class for checking the strength of a password."""
    
    def __init__(self):
        pass

    @staticmethod
    def check_password_strength(password):
        """
        Checks the strength of a given password.
        
        Args:
            password (str): The password to check.
        
        Returns:
            str: Strength of the password ("Weak", "Moderate", "Strong").
        
        Summary:
            Analyzes the given password and returns its strength based on length
            and character composition.
        """
        if len(password) < 6:
            return "Weak"
        elif len(password) >= 6 and any(char.isdigit() for char in password):
            return "Moderate"
        elif len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isupper() for char in password):
            return "Strong"
        else:
            return "Weak"

class FirewallRuleChecker:
    """Class for checking firewall rules."""
    
    def __init__(self):
        pass

    @staticmethod
    def check_firewall_rules():
        """
        Checks the current firewall rules.
        
        Returns:
            str: List of current firewall rules.
        
        Summary:
            Retrieves and returns the current firewall rules configured on the system.
        """
        result = subprocess.run(['sudo', 'iptables', '-L'], stdout=subprocess.PIPE)
        return result.stdout.decode()

class IPGeolocation:
    """Class for getting geolocation of an IP address."""
    
    def __init__(self):
        pass

    @staticmethod
    def get_geolocation(ip):
        """
        Gets the geolocation of a given IP address.
        
        Args:
            ip (str): The IP address to geolocate.
        
        Returns:
            dict: Geolocation information.
        
        Summary:
            Uses an external service to get and return the geolocation information
            for the specified IP address.
        """
        response = requests.get(f'http://ip-api.com/json/{ip}')
        return response.json()

class DataExfiltrationDetector:
    """Class for detecting data exfiltration."""
    
    def __init__(self):
        pass

    @staticmethod
    def detect_exfiltration(log_file, threshold=1000):
        """
        Detects potential data exfiltration.
        
        Args:
            log_file (str): The path to the log file.
            threshold (int): The threshold for data transfer in bytes.
        
        Returns:
            bool: True if exfiltration is detected, else False.
        
        Summary:
            Analyzes the specified log file for signs of data exfiltration based on
            the provided threshold and returns whether exfiltration is detected.
        """
        with open(log_file, 'r') as file:
            data_transferred = sum(int(line.split()[1]) for line in file)
        return data_transferred > threshold

class MalwareAnalyzer:
    """Class for analyzing malware samples."""
    
    def __init__(self):
        pass

    @staticmethod
    def analyze_malware(file_path):
        """
        Analyzes a given malware sample.
        
        Args:
            file_path (str): The path to the malware file.
        
        Returns:
            str: Analysis report.
        
        Summary:
            Analyzes the specified malware sample and returns an analysis report.
        """
        result = subprocess.run(['strings', file_path], stdout=subprocess.PIPE)
        return result.stdout.decode()

class SocialEngineeringDetector:
    """Class for detecting social engineering attacks."""
    
    def __init__(self):
        pass

    @staticmethod
    def detect_social_engineering(email_content):
        """
        Detects potential social engineering attacks.
        
        Args:
            email_content (str): The content of the email to analyze.
        
        Returns:
            bool: True if a social engineering attack is detected, else False.
        
        Summary:
            Analyzes the specified email content for signs of social engineering
            attacks and returns whether an attack is detected.
        """
        suspicious_keywords = ["urgent", "click here", "immediate action", "confidential"]
        return any(keyword in email_content.lower() for keyword in suspicious_keywords)

class PhishingURLDetector:
    """Class for detecting phishing URLs."""
    
    def __init__(self):
        pass

    @staticmethod
    def detect_phishing(url):
        """
        Detects if a URL is a phishing attempt.
        
        Args:
            url (str): The URL to check.
        
        Returns:
            bool: True if the URL is a phishing attempt, else False.
        
        Summary:
            Analyzes the specified URL to determine if it is a phishing attempt
            and returns the result.
        """
        phishing_keywords = ["login", "verify", "account", "secure"]
        return any(keyword in url.lower() for keyword in phishing_keywords)

class RansomwareDetector:
    """Class for detecting ransomware."""
    
    def __init__(self):
        pass

    @staticmethod
    def detect_ransomware(file_path):
        """
        Detects if a file is ransomware.
        
        Args:
            file_path (str): The path to the file.
        
        Returns:
            bool: True if the file is ransomware, else False.
        
        Summary:
            Analyzes the specified file to determine if it is ransomware and
            returns the result.
        """
        ransomware_signatures = ["ecbbf1c523f175282d807d073e07d54d"]
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        return file_hash in ransomware_signatures

class WirelessAuditor:
    """Class for auditing wireless networks."""
    
    def __init__(self):
        pass

    @staticmethod
    def audit_wireless(interface):
        """
        Audits wireless networks on a given interface.
        
        Args:
            interface (str): The wireless interface to audit.
        
        Returns:
            str: Audit report.
        
        Summary:
            Performs an audit of wireless networks using the specified interface
            and returns an audit report.
        """
        result = subprocess.run(['sudo', 'airodump-ng', interface], stdout=subprocess.PIPE)
        return result.stdout.decode()
