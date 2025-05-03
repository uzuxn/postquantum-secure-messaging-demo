# 🔐 postquantum-secure-messaging-demo-app -- Alice & Bob Secure Messaging

This Python GUI application demonstrates **Post-Quantum Cryptography concepts** using:
- **Elliptic Curve Cryptography (ECC)** for key exchange
- **AES-GCM** for secure message encryption
- A modern **Tkinter UI** for two users: Alice (Sender) and Bob (Receiver)

## 💡 Project Highlights

- 🔐 ECC key generation using P-256 curve
- 🔑 Shared key derivation with HKDF
- 🔒 AES-GCM encryption for confidentiality and integrity
- 📤 Alice encrypts and sends a message to Bob
- 🔓 Bob receives, decrypts, and views the message
- 📝 Message history tracking for both users
- 🌈 Polished and user-friendly UI with sections and color coding

---

## 📦 Dependencies

Install the required libraries via `pip`:

```bash
pip install pycryptodome
