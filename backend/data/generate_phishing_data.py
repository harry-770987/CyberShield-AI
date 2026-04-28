import os
import random
import pandas as pd
import re

def generate_phishing_data(num_samples: int = 15000, output_path: str = "phishing_data.csv"):
    """
    Generates synthetic phishing URLs and email bodies.
    50% legitimate, 50% phishing.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    legit_domains = ["google.com", "amazon.com", "github.com", "microsoft.com", "apple.com", "netflix.com", "linkedin.com"]
    phish_domains = ["secure-login-update.com", "verify-account-info.xyz", "apple-id-support.tk", "paypal-security.ml", "amazon-free-gift.cc"]
    
    legit_emails = [
        "Your order #12345 has shipped. Click here to track your package.",
        "Hi team, just a reminder about our meeting at 2 PM today. Please review the attached document.",
        "Thanks for subscribing to our newsletter! Here are the top stories for this week.",
        "Your account statement for this month is now available online.",
        "Can we reschedule our call to next Thursday? Let me know."
    ]
    
    phish_emails = [
        "URGENT: Verify your account immediately or it will be suspended in 24 hours.",
        "Congratulations! You have won a $1000 gift card. Click here to claim your prize now.",
        "Unusual sign-in activity detected on your account. Please secure your account by logging in here.",
        "Your invoice #9981 is overdue. Download the attachment to view the details and pay.",
        "Dear customer, your bank account is compromised. Click this link to avoid suspension."
    ]
    
    data = []
    
    for _ in range(num_samples):
        is_phishing = random.random() < 0.5
        
        if is_phishing:
            domain = random.choice(phish_domains)
            # Add IP or weird subdomains
            if random.random() < 0.2:
                url = f"http://{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}/login.php"
            else:
                sub = "-".join([random.choice(["secure", "login", "update", "verify"]) for _ in range(random.randint(1,3))])
                url = f"http://{sub}.{domain}/auth/verify?token=123"
            email = random.choice(phish_emails)
            label = 1
        else:
            domain = random.choice(legit_domains)
            url = f"https://www.{domain}/{random.choice(['index', 'home', 'about', 'contact'])}"
            email = random.choice(legit_emails)
            label = 0
            
        # Extract features locally (the generator does this so we have truth)
        url_length = len(url)
        num_dots = url.count('.')
        num_hyphens = url.count('-')
        num_at = url.count('@')
        num_digits = len(re.findall(r'\d', url))
        has_ip = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0
        is_https = 1 if url.startswith('https') else 0
        domain_part = url.split('/')[2] if len(url.split('/')) > 2 else url
        subdomain_count = domain_part.count('.') - 1 if not has_ip else 0
        suspicious_words = ['login', 'verify', 'update', 'secure', 'account', 'free', 'bonus']
        suspicious_words_count = sum(1 for w in suspicious_words if w in url.lower())
        domain_length = len(domain_part)
        
        data.append({
            'url': url,
            'email_body': email,
            'url_length': url_length,
            'num_dots': num_dots,
            'num_hyphens': num_hyphens,
            'num_at': num_at,
            'num_digits': num_digits,
            'has_ip': has_ip,
            'is_https': is_https,
            'subdomain_count': subdomain_count,
            'suspicious_words_count': suspicious_words_count,
            'domain_length': domain_length,
            'label': label
        })
        
    pd.DataFrame(data).to_csv(output_path, index=False)
    print(f"Generated {num_samples} phishing samples at {output_path}")

if __name__ == "__main__":
    generate_phishing_data(15000, "data/phishing_data.csv")
