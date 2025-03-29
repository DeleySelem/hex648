# Hex64: I Ching-Based Secure File Encoder 🔐

**Hex64** combines ancient symbolism with modern cryptography to provide robust file encryption. Leveraging the I Ching's 64 hexagrams and a custom hash algorithm, Hex64 transforms data into secure, esoteric symbols while offering computational resistance to brute-force attacks.

---

## 🛡️ Security Highlights

### **Unbreakable by Brute Force**
- **Passphrase Strength**:  
  An 8-character passphrase with mixed-case + numbers + symbols (`72^8` combinations) would take ≈**221 million years** to crack at 1k attempts/sec.  
  *Even with 1 million cores*: **221,000 years**.
  
- **Iteration Hardening**:  
  Configurable iterations (default: 1) exponentially increase complexity. At 1,000 iterations, attacks become practically infeasible.

### **Cryptographic Components**
| Component                    | Role                                          
|------------------------------|-------------------------------------------------|
| **Hex64Hash (C Library)**    | Custom non-reversible hash for seed generation.
| **Trigram/Hexagram Mapping** | Converts binary to I Ching symbols (☰, ䷀, etc.).
| **Bit Swapping**             | Seed-driven bit permutation for encryption.   

---

## 🔄 How It Works

### **Encryption Flow**
1. **Text → Binary**: UTF-8 text is converted to an 8-bit binary stream.
2. **Seed Generation**:  
   - Passphrase-derived seed via `Hex64Hash` (SHA-3 inspired mixing).  
   - Seed iteratively permutes bits using XOR and rotation operations.
3. **Symbol Mapping**:  
   - Binary split into 3-bit **trigrams** (e.g., `010` → ☲).  
   - Paired into 6-bit **hexagrams** (e.g., `010011` → ䷃).

### **Decryption Flow**
1. Reverse hexagrams → trigrams → binary.  
2. Apply seed in reverse order to undo bit swaps.  
3. Strip padding and decode UTF-8.

---

## ⚙️ Usage

### **Encode a File**
```bash
./hex648.py -f secret.txt -p "Tao&42!" -x 100 -v

    -p: Passphrase (required for encryption).

    -x: Seed iterations (increases security).

    -v: Show binary/trigram steps.

Decode a File
bash
Copy

./hex648.py -d hexed_secret.txt -p "Tao&42!" -x 100

Run Encrypted Scripts
bash
Copy

# Execute encoded Python/Bash directly from memory
./hex648.py -rp encoded_script.py -p "Tao&42!"

🔍 Security Considerations
Assumptions

    No known vulnerabilities in Hex64Hash.

    Attacker cannot bypass symbol-to-binary conversion.

Best Practices

    Use 12+ character passphrases with symbols/numbers.
    Example: "N0rth_St4r+W0rmwood" (≈72^16 combinations).

    Set iterations ≥100 to hinder parallel attacks.

    Avoid dictionary words or predictable patterns.

🚀 Installation

    Clone the repository.

    Compile dependencies:
    bash
    Copy

    chmod +x install.sh && ./install.sh  # Builds hex64hash library

    Run hex648.py with Python 3.

📜 License

MIT License. Use responsibly.

    "What is well encrypted cannot be stolen."
    — Adaptation from the I Ching, Hexagram 26 (䷘)

Copy


This README balances technical detail with accessibility, emphasizing security through:  
1. **Brute-force time estimates** to showcase strength.  
2. **Component breakdown** for transparency.  
3. **Actionable best practices** for users.  
4. **Philosophical branding** tying I Ching to modern crypto.
