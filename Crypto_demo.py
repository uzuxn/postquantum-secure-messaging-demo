import tkinter as tk
from tkinter import ttk
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
import base64
import threading


class Shared:
    alice_pub = None
    alice_priv = None
    bob_pub = None
    bob_priv = None
    encrypted_msg = None
    nonce = None
    tag = None
    bob_encrypted_input = None
    alice_history = None
    bob_history = None

shared = Shared()


def encrypt_aes(message, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return ciphertext, cipher.nonce, tag

def decrypt_aes(ciphertext, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def derive_shared_key(priv_key, pub_key):
    secret = priv_key.d * pub_key.pointQ
    x_bytes = int(secret.x).to_bytes(32, 'big')
    return HKDF(x_bytes, 32, b'', SHA256)

# Alice
def alice_window():
    win = tk.Tk()
    win.title("🔐 Alice - Crypto Demo")
    win.geometry("600x540")
    win.configure(bg="#f0f4f8")

    style = ttk.Style()
    style.theme_use("clam")

    header = tk.Label(win, text="Alice - Sender", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50")
    header.pack(pady=10)

    def section_label(text):
        return tk.Label(win, text=text, font=("Helvetica", 12, "bold"), bg="#f0f4f8", anchor="w", fg="#34495e")

    def gen_keys():
        shared.alice_priv = ECC.generate(curve='P-256')
        shared.alice_pub = shared.alice_priv.public_key()
        status.config(text="✅ Alice's keys generated.")

    def encrypt_msg():
        if shared.bob_pub is None:
            status.config(text="❌ Bob's public key not available.")
            return
        message = msg_entry.get("1.0", tk.END).strip().encode()
        key = derive_shared_key(shared.alice_priv, shared.bob_pub)
        ct, nonce, tag = encrypt_aes(message, key)
        shared.encrypted_msg = ct
        shared.nonce = nonce
        shared.tag = tag

        b64_msg = base64.b64encode(ct).decode()
        enc_output.delete("1.0", tk.END)
        enc_output.insert(tk.END, b64_msg)
        status.config(text="✅ Message encrypted and sent.")

        shared.alice_history.insert(tk.END, f"You ➤ {message.decode()}\nEncrypted ➤ {b64_msg}\n\n")

        if shared.bob_encrypted_input:
            shared.bob_encrypted_input.delete("1.0", tk.END)
            shared.bob_encrypted_input.insert(tk.END, b64_msg)

    ttk.Button(win, text="Generate Keys", command=gen_keys).pack(pady=5)
    section_label("Message to Bob").pack()
    msg_entry = tk.Text(win, height=4, bg="#ffffff", fg="#2c3e50", font=("Courier", 10))
    msg_entry.pack(padx=10, fill=tk.X)

    ttk.Button(win, text="Encrypt & Send", command=encrypt_msg).pack(pady=5)
    section_label("Encrypted Output (Base64)").pack()
    enc_output = tk.Text(win, height=3, bg="#fefefe", fg="#2c3e50", font=("Courier", 10))
    enc_output.pack(padx=10, fill=tk.X)

    section_label("Message History").pack(pady=(10, 0))
    history_frame = tk.Frame(win, bg="#f0f4f8")
    history_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    history = tk.Text(history_frame, height=10, bg="#ffffff", font=("Courier", 10), wrap=tk.WORD)
    history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(history_frame, command=history.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    history.config(yscrollcommand=scrollbar.set)
    shared.alice_history = history

    status = tk.Label(win, text="", bg="#f0f4f8", fg="#16a085", font=("Helvetica", 10))
    status.pack(pady=5)

    win.mainloop()

# Bob
def bob_window():
    win = tk.Tk()
    win.title("🔓 Bob - Crypto Demo")
    win.geometry("600x540")
    win.configure(bg="#f0f4f8")

    header = tk.Label(win, text="Bob - Receiver", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50")
    header.pack(pady=10)

    def section_label(text):
        return tk.Label(win, text=text, font=("Helvetica", 12, "bold"), bg="#f0f4f8", anchor="w", fg="#34495e")

    def gen_keys():
        shared.bob_priv = ECC.generate(curve='P-256')
        shared.bob_pub = shared.bob_priv.public_key()
        status.config(text="✅ Bob's keys generated.")

    def decrypt_msg():
        if not shared.encrypted_msg or not shared.nonce:
            status.config(text="❌ No message received.")
            return
        try:
            key = derive_shared_key(shared.bob_priv, shared.alice_pub)
            plain = decrypt_aes(shared.encrypted_msg, key, shared.nonce, shared.tag)
            dec_output.delete("1.0", tk.END)
            dec_output.insert(tk.END, plain.decode())
            status.config(text="✅ Decryption successful.")
            shared.bob_history.insert(tk.END, f"Alice ➤ {plain.decode()}\n\n")
        except:
            status.config(text="❌ Decryption failed!")

    ttk.Button(win, text="Generate Keys", command=gen_keys).pack(pady=5)
    section_label("Encrypted Message (Auto-Received)").pack()
    encrypted_input = tk.Text(win, height=3, bg="#fefefe", fg="#2c3e50", font=("Courier", 10))
    encrypted_input.pack(padx=10, fill=tk.X)
    shared.bob_encrypted_input = encrypted_input

    ttk.Button(win, text="Decrypt Message", command=decrypt_msg).pack(pady=5)
    section_label("Decrypted Message").pack()
    dec_output = tk.Text(win, height=3, bg="#ffffff", fg="#2c3e50", font=("Courier", 10))
    dec_output.pack(padx=10, fill=tk.X)

    section_label("Message History").pack(pady=(10, 0))
    history_frame = tk.Frame(win, bg="#f0f4f8")
    history_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    history = tk.Text(history_frame, height=10, bg="#ffffff", font=("Courier", 10), wrap=tk.WORD)
    history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(history_frame, command=history.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    history.config(yscrollcommand=scrollbar.set)
    shared.bob_history = history

    status = tk.Label(win, text="", bg="#f0f4f8", fg="#16a085", font=("Helvetica", 10))
    status.pack(pady=5)

    win.mainloop()


if __name__ == "__main__":
    threading.Thread(target=alice_window, daemon=True).start()
    threading.Thread(target=bob_window, daemon=True).start()
    while True:
        pass
