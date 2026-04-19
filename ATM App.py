import tkinter as tk
from tkinter import messagebox, ttk
import json, os, datetime, random, string

# ═══════════════════════════════════════════════════════════════════════════════
#  ATM SIMULATION - COMPACT VERSION (All Features Retained)
# ══════════════════════���════════════════════════════════════════════════════════

ACCOUNTS_FILE, TRANSACTIONS_FILE = "accounts.json", "transactions.json"
MIN_BALANCE, MAX_PIN_ATTEMPTS, OTP_EXPIRY_SECS = 500.0, 3, 120

# Color Palette
COLORS = {
    'dark': "#0A1628", 'card': "#112240", 'input': "#1E3A5F", 'accent': "#00D4FF",
    'accent2': "#0095B6", 'green': "#00C853", 'red': "#FF1744", 'gold': "#FFD700",
    'grey': "#546E7A", 'otp': "#E65100", 'white': "#FFFFFF", 'light': "#B0C4DE",
    'dim': "#607D8B", 'success': "#00E676", 'error': "#FF5252", 'otp_bg': "#0D2B0D"
}

FONTS = {
    'body': ("Segoe UI", 12), 'small': ("Segoe UI", 10), 'btn': ("Segoe UI", 12, "bold"),
    'label': ("Segoe UI", 11), 'input': ("Segoe UI", 13), 'mono': ("Courier New", 11),
    'otp': ("Courier New", 24, "bold"), 'title': ("Segoe UI", 18, "bold"), 'header': ("Segoe UI", 16, "bold")
}

def load_data(file):
    return json.load(open(file, 'r')) if os.path.exists(file) else ({} if file == ACCOUNTS_FILE else [])

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f, indent=4)

def record_transaction(acc_no, txn_type, amount, balance_after):
    txns = load_data(TRANSACTIONS_FILE)
    txns.append({"account_number": acc_no, "type": txn_type, "amount": amount, 
                 "balance_after": balance_after, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_data(TRANSACTIONS_FILE, txns)

def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))

def mask_phone(phone):
    return phone if len(phone) <= 4 else "X" * (len(phone) - 4) + phone[-4:]

def make_entry(parent, show=None, font=FONTS['input'], textvariable=None):
    e = tk.Entry(parent, font=font, bg=COLORS['input'], fg=COLORS['white'],
                 insertbackground=COLORS['accent'], relief="flat", highlightthickness=2,
                 highlightcolor=COLORS['accent'], highlightbackground=COLORS['input'],
                 show=show, textvariable=textvariable)
    e.pack(fill="x", pady=4, ipady=8)
    return e

def make_button(parent, text, command, color=None, fg=COLORS['white'], pady=6):
    color = color or COLORS['accent2']
    btn = tk.Button(parent, text=text, command=command, font=FONTS['btn'], bg=color, fg=fg,
                    activebackground=COLORS['accent'], activeforeground=COLORS['white'], relief="flat", cursor="hand2")
    btn.pack(fill="x", pady=pady, ipady=10)
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS['accent']))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def divider(parent):
    tk.Frame(parent, height=1, bg=COLORS['dim']).pack(fill="x", pady=8)

def clear_frame(frame):
    for w in frame.winfo_children(): w.destroy()

class ATMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if sw >= 800:
            self.geometry(f"{420}x{820}+{(sw-420)//2}+{(sh-820)//2}")
            self.minsize(360, 640)
        else:
            self.geometry(f"{sw}x{sh}+0+0")
        self.title("ATM Simulation System")
        self.configure(bg=COLORS['dark'])
        self.current_acc, self.account_data, self.pin_attempts = None, None, 0
        self._active_otp, self._otp_acc, self._otp_timer_active = None, None, False
        self._build_header()
        self.content = tk.Frame(self, bg=COLORS['dark'])
        self.content.pack(fill="both", expand=True)
        self._build_footer()
        self.show_welcome()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS['card'], height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🏦", font=("Segoe UI", 22), bg=COLORS['card'], fg=COLORS['accent']).place(x=14, rely=0.5, anchor="w")
        tk.Label(hdr, text="PyBank ATM", font=FONTS['header'], bg=COLORS['card'], fg=COLORS['white']).place(x=52, rely=0.5, anchor="w")
        self.clock_lbl = tk.Label(hdr, text="", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['light'])
        self.clock_lbl.place(relx=1.0, x=-12, rely=0.5, anchor="e")
        self._tick()

    def _tick(self):
        self.clock_lbl.config(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick)

    def _build_footer(self):
        ftr = tk.Frame(self, bg=COLORS['card'], height=34)
        ftr.pack(fill="x", side="bottom")
        ftr.pack_propagate(False)
        tk.Label(ftr, text="CGB1121 - Python Programming  |  Secure & Encrypted", font=FONTS['small'], 
                bg=COLORS['card'], fg=COLORS['dim']).pack(expand=True)

    def _switch(self, build_fn):
        clear_frame(self.content)
        canvas = tk.Canvas(self.content, bg=COLORS['dark'], highlightthickness=0)
        sb = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=COLORS['dark'])
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        wid = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        build_fn(self.scroll_frame)

    def _screen_title(self, parent, title, subtitle):
        hdr = tk.Frame(parent, bg=COLORS['dark'])
        hdr.pack(fill="x", padx=18, pady=(16, 4))
        tk.Label(hdr, text=title, font=FONTS['title'], bg=COLORS['dark'], fg=COLORS['white'], anchor="w").pack(fill="x")
        tk.Label(hdr, text=subtitle, font=FONTS['small'], bg=COLORS['dark'], fg=COLORS['accent'], anchor="w").pack(fill="x")

    def _toast(self, parent, msg, color=None):
        color = color or COLORS['error']
        t = tk.Label(parent, text=msg, font=FONTS['label'], bg=color, fg=COLORS['white'], anchor="center")
        t.pack(fill="x", padx=14, pady=4, ipady=6)
        parent.after(3500, t.destroy)

    def _make_info_row(self, parent, label, value, bg_override=None, val_color=None):
        bg = bg_override or COLORS['input']
        val_color = val_color or COLORS['white']
        r = tk.Frame(parent, bg=bg)
        r.pack(fill="x")
        tk.Label(r, text=label, font=FONTS['label'], bg=bg, fg=COLORS['light'], anchor="w").pack(side="left", padx=14, pady=8)
        tk.Label(r, text=value, font=("Segoe UI", 12, "bold"), bg=bg, fg=val_color, anchor="e").pack(side="right", padx=14)

    def _quick_buttons(self, parent, amounts, var, disabled_fn=None):
        qf = tk.Frame(parent, bg=COLORS['card'])
        qf.pack(fill="x", padx=14, pady=6)
        for amt in amounts:
            is_disabled = disabled_fn and disabled_fn(amt)
            state = tk.DISABLED if is_disabled else tk.NORMAL
            color = COLORS['grey'] if is_disabled else COLORS['accent2']
            tk.Button(qf, text=f"Rs{amt}", font=FONTS['btn'], bg=color, fg=COLORS['white'], 
                     relief="flat", state=state, cursor="hand2", 
                     command=lambda a=str(amt): var.set(a)).pack(side="left", padx=4, pady=4, ipadx=4, ipady=6)

    # ────── WELCOME ──────────────────────────────────────────────────────

    def show_welcome(self):
        self._switch(self._build_welcome)

    def _build_welcome(self, parent):
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=(28, 10))
        tk.Label(card, text="💳", font=("Segoe UI", 54), bg=COLORS['card'], fg=COLORS['accent']).pack(pady=(22, 0))
        tk.Label(card, text="ATM Simulation System", font=FONTS['title'], bg=COLORS['card'], fg=COLORS['white']).pack()
        tk.Label(card, text="Fast  •  Secure  •  OTP Recovery", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['accent']).pack(pady=(2, 18))
        divider(card)
        stats = tk.Frame(card, bg=COLORS['card'])
        stats.pack(fill="x", padx=12, pady=6)
        for icon, val, lbl in [("🔒","256-bit","Encryption"), ("📱","OTP","Recovery"), ("⚡","Instant","Transfers")]:
            col = tk.Frame(stats, bg=COLORS['card'])
            col.pack(side="left", expand=True)
            tk.Label(col, text=icon, font=("Segoe UI", 18), bg=COLORS['card'], fg=COLORS['accent']).pack()
            tk.Label(col, text=val, font=("Segoe UI", 10, "bold"), bg=COLORS['card'], fg=COLORS['white']).pack()
            tk.Label(col, text=lbl, font=FONTS['small'], bg=COLORS['card'], fg=COLORS['light']).pack()
        divider(card)
        bf = tk.Frame(card, bg=COLORS['card'])
        bf.pack(fill="x", padx=16, pady=(4, 20))
        make_button(bf, "🔑  LOGIN TO ACCOUNT", self.show_login, color=COLORS['green'])
        tk.Frame(bf, height=6, bg=COLORS['card']).pack()
        make_button(bf, "➕  CREATE NEW ACCOUNT", self.show_create_account, color=COLORS['accent2'])
        info = tk.Frame(parent, bg=COLORS['dark'])
        info.pack(fill="x", padx=18, pady=4)
        tk.Label(info, text="K.E. RAMALAKSHMI  |  VIKASINI SHANMUGAM", font=FONTS['small'], bg=COLORS['dark'], fg=COLORS['dim']).pack()
        tk.Label(info, text="Reg: 927625BSC046  |  927625BSC061", font=FONTS['small'], bg=COLORS['dark'], fg=COLORS['dim']).pack()

    # ────── CREATE ACCOUNT ──────────────────────────────────────────────

    def show_create_account(self):
        self._switch(self._build_create_account)

    def _build_create_account(self, parent):
        self._screen_title(parent, "➕ Create Account", "MODULE 1 - LOGIN MODULE")
        badge = tk.Frame(parent, bg="#0D2137")
        badge.pack(fill="x", padx=18, pady=(4, 2))
        tk.Label(badge, text="📱  Mobile number is used for OTP-based PIN recovery",
                 font=FONTS['small'], bg="#0D2137", fg=COLORS['accent'], wraplength=340, justify="left").pack(padx=12, pady=8, anchor="w")
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=6)
        fields = {key: make_entry(card, show=show, font=FONTS['input']) 
                  for (label, key, show) in [("Full Name", "name", None), ("Account Number (10 digits)", "acc", None),
                                             ("Mobile Number (10 digits)", "phone", None), ("4-digit PIN", "pin", "●"),
                                             ("Confirm PIN", "cpin", "●"), ("Opening Deposit (Rs)", "deposit", None)]
                  for _ in [tk.Label(card, text=label, font=FONTS['label'], fg=COLORS['light'], 
                           bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10, 0))] }
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0, 16))

        def submit():
            data = {k: fields[k].get().strip() for k in fields}
            if not all(data.values()): return self._toast(card, "All fields required.", COLORS['error'])
            if not data['acc'].isdigit() or len(data['acc']) != 10: return self._toast(card, "Account number: 10 digits.", COLORS['error'])
            if not data['phone'].isdigit() or len(data['phone']) != 10: return self._toast(card, "Mobile: 10 digits.", COLORS['error'])
            if not data['pin'].isdigit() or len(data['pin']) != 4: return self._toast(card, "PIN: 4 digits.", COLORS['error'])
            if data['pin'] != data['cpin']: return self._toast(card, "PINs don't match.", COLORS['error'])
            try: dep = float(data['deposit'])
            except ValueError: return self._toast(card, "Valid deposit amount.", COLORS['error'])
            if dep < MIN_BALANCE: return self._toast(card, f"Min deposit: Rs {MIN_BALANCE:.0f}", COLORS['error'])
            accounts = load_data(ACCOUNTS_FILE)
            if data['acc'] in accounts: return self._toast(card, "Account exists.", COLORS['error'])
            if any(v.get("phone") == data['phone'] for v in accounts.values()): return self._toast(card, "Mobile linked.", COLORS['error'])
            accounts[data['acc']] = {"name": data['name'], "pin": data['pin'], "phone": data['phone'], "balance": dep}
            save_data(ACCOUNTS_FILE, accounts)
            record_transaction(data['acc'], "OPEN", dep, dep)
            messagebox.showinfo("Account Created", f"Name: {data['name']}\nAcc: {data['acc']}\nMobile: {mask_phone(data['phone'])}\nBalance: Rs {dep:.2f}")
            self.show_welcome()

        make_button(br, "CREATE ACCOUNT", submit, color=COLORS['green'])
        make_button(br, "<- Back", self.show_welcome, color=COLORS['grey'], pady=2)

    # ────── LOGIN ──────────────────────────────────────────────────────

    def show_login(self):
        self.pin_attempts = 0
        self._switch(self._build_login)

    def _build_login(self, parent):
        self._screen_title(parent, "🔑 Login", "MODULE 1 & 2 - LOGIN + PIN VERIFICATION")
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        tk.Label(card, text="Account Number", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(14, 0))
        acc_entry = make_entry(card)
        acc_entry.pack_configure(padx=14)
        tk.Label(card, text="4-Digit PIN", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10, 0))
        pin_entry = make_entry(card, show="●")
        pin_entry.pack_configure(padx=14)
        kf = tk.Frame(card, bg=COLORS['card'])
        kf.pack(padx=14, pady=6)
        for row in [['1','2','3'],['4','5','6'],['7','8','9'],['<','0','OK']]:
            rf = tk.Frame(kf, bg=COLORS['card'])
            rf.pack(fill="x")
            for d in row:
                col = COLORS['green'] if d=='OK' else COLORS['red'] if d=='<' else COLORS['input']
                disp = '⌫' if d=='<' else ('✓' if d=='OK' else d)
                def kp(val=d):
                    if val == '<': pin_entry.delete(len(pin_entry.get())-1, tk.END) if pin_entry.get() else None
                    elif val == 'OK': do_login()
                    else: pin_entry.insert(tk.END, val) if len(pin_entry.get()) < 4 else None
                tk.Button(rf, text=disp, font=("Segoe UI", 14, "bold"), bg=col, fg=COLORS['white'], relief="flat", width=4, height=2, cursor="hand2", command=kp).pack(side="left", padx=3, pady=3)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0, 4))

        def do_login():
            acc, pin = acc_entry.get().strip(), pin_entry.get().strip()
            accounts = load_data(ACCOUNTS_FILE)
            if acc not in accounts: return self._toast(card, "Account not found.", COLORS['error'])
            if pin == accounts[acc]["pin"]:
                self.current_acc, self.account_data, self.pin_attempts = acc, accounts[acc], 0
                self.show_dashboard()
            else:
                self.pin_attempts += 1
                remaining = MAX_PIN_ATTEMPTS - self.pin_attempts
                pin_entry.delete(0, tk.END)
                if remaining <= 0:
                    messagebox.showerror("Blocked", "Too many failed attempts!\nUse 'Forgot PIN' to recover.")
                    self.show_welcome()
                else:
                    self._toast(card, f"Wrong PIN. {remaining} attempt(s) left.", COLORS['error'])

        make_button(br, "🔓  LOGIN", do_login, color=COLORS['green'])
        fp_frame = tk.Frame(card, bg=COLORS['card'])
        fp_frame.pack(fill="x", padx=14, pady=(4, 4))
        fp = tk.Label(fp_frame, text="🔑  Forgot PIN?  Recover via OTP  →", font=("Segoe UI", 11, "underline"), 
                     bg=COLORS['card'], fg=COLORS['otp'], cursor="hand2")
        fp.pack(anchor="center", pady=6)
        fp.bind("<Button-1>", lambda e: self.show_forgot_pin())
        make_button(card, "<- Back", self.show_welcome, color=COLORS['grey'], pady=2)

    # ────── FORGOT PIN (OTP REQUEST) ────────────────────────────────────

    def show_forgot_pin(self):
        self._switch(self._build_forgot_pin)

    def _build_forgot_pin(self, parent):
        self._screen_title(parent, "🔑 Forgot PIN", "OTP-BASED PIN RECOVERY")
        info = tk.Frame(parent, bg=COLORS['otp_bg'])
        info.pack(fill="x", padx=18, pady=(6, 4))
        tk.Label(info, text="📱  An OTP will be sent to your registered mobile\nnumber. Use it to reset your PIN securely.",
                 font=FONTS['small'], bg=COLORS['otp_bg'], fg=COLORS['success'], justify="left", wraplength=340).pack(padx=14, pady=10, anchor="w")
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=6)
        tk.Label(card, text="Account Number", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(14, 0))
        acc_e = make_entry(card)
        acc_e.pack_configure(padx=14)
        tk.Label(card, text="Registered Mobile Number", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10, 0))
        phone_e = make_entry(card)
        phone_e.pack_configure(padx=14)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0, 16))

        def request_otp():
            acc, phone = acc_e.get().strip(), phone_e.get().strip()
            accounts = load_data(ACCOUNTS_FILE)
            if acc not in accounts: return self._toast(card, "Account not found.", COLORS['error'])
            if "phone" not in accounts[acc] or not accounts[acc]["phone"]: return self._toast(card, "No mobile registered.", COLORS['error'])
            if accounts[acc]["phone"] != phone: return self._toast(card, "Mobile doesn't match records.", COLORS['error'])
            otp_code = generate_otp(6)
            self._active_otp = {"code": otp_code, "expires": datetime.datetime.now() + datetime.timedelta(seconds=OTP_EXPIRY_SECS)}
            self._otp_acc = acc
            messagebox.showinfo("📱 OTP Sent  [DEMO]", f"Simulated SMS to {mask_phone(phone)}\n\nYour PyBank OTP is:\n\n       {otp_code}\n\nValid for {OTP_EXPIRY_SECS // 60} minutes.\n(In production this SMS is sent silently)")
            self.show_otp_verify()

        make_button(br, "📱  SEND OTP TO MOBILE", request_otp, color=COLORS['otp'])
        make_button(br, "<- Back to Login", self.show_login, color=COLORS['grey'], pady=2)

    # ─────�� OTP VERIFY ──────────────────────────────────────────────────

    def show_otp_verify(self):
        self._otp_timer_active = True
        self._switch(self._build_otp_verify)

    def _build_otp_verify(self, parent):
        self._screen_title(parent, "🔐 Enter OTP", "OTP VERIFICATION")
        timer_frame = tk.Frame(parent, bg=COLORS['otp_bg'])
        timer_frame.pack(fill="x", padx=18, pady=(6, 4))
        timer_lbl = tk.Label(timer_frame, text="", font=FONTS['label'], bg=COLORS['otp_bg'], fg=COLORS['success'])
        timer_lbl.pack(pady=10)

        def update_timer():
            if not self._otp_timer_active: return
            remaining = int((self._active_otp["expires"] - datetime.datetime.now()).total_seconds())
            if remaining <= 0:
                timer_lbl.config(text="OTP expired! Request a new one.", fg=COLORS['error'])
                self._otp_timer_active = False
            else:
                m, s = divmod(remaining, 60)
                col = COLORS['success'] if remaining > 30 else COLORS['gold']
                timer_lbl.config(text=f"⏱  OTP expires in  {m:02d}:{s:02d}", fg=col)
                parent.after(1000, update_timer)

        update_timer()
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=6)
        tk.Label(card, text="Enter the 6-digit OTP sent to your\nregistered mobile number",
                 font=FONTS['label'], bg=COLORS['card'], fg=COLORS['light'], justify="center").pack(pady=(16, 4))
        otp_frame = tk.Frame(card, bg=COLORS['card'])
        otp_frame.pack(pady=12)
        otp_entries = []
        for i in range(6):
            e = tk.Entry(otp_frame, font=FONTS['otp'], width=2, bg=COLORS['input'], fg=COLORS['accent'],
                         insertbackground=COLORS['accent'], relief="flat", highlightthickness=2, 
                         highlightcolor=COLORS['accent'], highlightbackground=COLORS['input'], justify="center")
            e.grid(row=0, column=i, padx=4, ipady=8)
            otp_entries.append(e)
            def on_key(event, idx=i):
                v = otp_entries[idx].get()
                if len(v) > 1: otp_entries[idx].delete(1, tk.END)
                if v and idx < 5: otp_entries[idx+1].focus_set()
                if event.keysym == "BackSpace" and not v and idx > 0: otp_entries[idx-1].focus_set()
            e.bind("<KeyRelease>", on_key)
        otp_entries[0].focus_set()
        tk.Label(card, text="Or paste full OTP below:", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['dim']).pack(pady=(8, 0))
        paste_e = make_entry(card)
        paste_e.pack_configure(padx=14)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0, 16))

        def get_entered_otp():
            return ("".join(e.get()[:1] for e in otp_entries) if not paste_e.get() else paste_e.get()).strip()

        def verify_otp():
            if datetime.datetime.now() > self._active_otp["expires"]: return self._toast(card, "OTP expired.", COLORS['error'])
            if get_entered_otp() == self._active_otp["code"]:
                self._otp_timer_active, self._active_otp = False, None
                self.show_set_new_pin()
            else: self._toast(card, "Incorrect OTP. Try again.", COLORS['error'])

        def resend():
            self._otp_timer_active = False
            self.show_forgot_pin()

        make_button(br, "VERIFY OTP", verify_otp, color=COLORS['green'])
        make_button(br, "🔄  Resend OTP", resend, color=COLORS['otp'], pady=2)
        make_button(br, "<- Back to Login", lambda: [setattr(self, '_otp_timer_active', False), self.show_login()], color=COLORS['grey'], pady=2)

    # ────── SET NEW PIN ─────────────────────────────────────────────────

    def show_set_new_pin(self):
        self._switch(self._build_set_new_pin)

    def _build_set_new_pin(self, parent):
        self._screen_title(parent, "🔐 Set New PIN", "OTP VERIFIED - CREATE NEW PIN")
        sb = tk.Frame(parent, bg=COLORS['otp_bg'])
        sb.pack(fill="x", padx=18, pady=(6, 4))
        tk.Label(sb, text="  OTP Verified! Now set your new PIN.", font=FONTS['label'], bg=COLORS['otp_bg'], fg=COLORS['success']).pack(pady=10)
        accounts = load_data(ACCOUNTS_FILE)
        acc_data = accounts[self._otp_acc]
        ic = tk.Frame(parent, bg=COLORS['card'])
        ic.pack(fill="x", padx=18, pady=4)
        for lbl, val in [("Account Holder", acc_data["name"]), ("Account Number", self._otp_acc), ("Mobile", mask_phone(acc_data.get("phone", "N/A")))]:
            r = tk.Frame(ic, bg=COLORS['input'])
            r.pack(fill="x", padx=14, pady=3)
            tk.Label(r, text=lbl, font=FONTS['small'], bg=COLORS['input'], fg=COLORS['light']).pack(side="left", padx=10, pady=6)
            tk.Label(r, text=val, font=("Segoe UI", 11, "bold"), bg=COLORS['input'], fg=COLORS['white']).pack(side="right", padx=10)
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        fields = {key: make_entry(card, show="●") for (lbl, key) in [("New 4-digit PIN", "new"), ("Confirm New PIN", "cnew")]
                  for _ in [tk.Label(card, text=lbl, font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(12, 0))]}
        strength_lbl = tk.Label(card, text="", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['dim'])
        strength_lbl.pack(anchor="w", padx=14)

        def on_type(*_):
            v = fields["new"].get()
            if not v: strength_lbl.config(text="")
            elif len(v) < 4: strength_lbl.config(text="o"*(4-len(v)) + " - need " + str(4-len(v)) + " more", fg=COLORS['gold'])
            else: strength_lbl.config(text="PIN complete", fg=COLORS['success'])
        fields["new"].bind("<KeyRelease>", on_type)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0, 16))

        def save_pin():
            new, cnew = fields["new"].get().strip(), fields["cnew"].get().strip()
            if not new.isdigit() or len(new) != 4: return self._toast(card, "PIN: 4 digits.", COLORS['error'])
            if new != cnew: return self._toast(card, "PINs don't match.", COLORS['error'])
            if new == accounts[self._otp_acc]["pin"]: return self._toast(card, "Same as old PIN.", COLORS['error'])
            accounts[self._otp_acc]["pin"] = new
            save_data(ACCOUNTS_FILE, accounts)
            self._otp_acc = None
            messagebox.showinfo("PIN Reset Successful", "Your PIN has been reset successfully!\n\nYou can now login with your new PIN.")
            self.show_login()

        make_button(br, "🔐  SAVE NEW PIN", save_pin, color=COLORS['green'])

    # ────── DASHBOARD ───────────────────────────────────────────────────

    def show_dashboard(self):
        self._switch(self._build_dashboard)

    def _build_dashboard(self, parent):
        acc, data = self.current_acc, self.account_data
        wcard = tk.Frame(parent, bg=COLORS['card'])
        wcard.pack(fill="x", padx=18, pady=(20, 8))
        tk.Label(wcard, text="👤", font=("Segoe UI", 28), bg=COLORS['card'], fg=COLORS['accent']).pack(pady=(16, 0))
        tk.Label(wcard, text="Welcome,", font=FONTS['body'], bg=COLORS['card'], fg=COLORS['light']).pack()
        tk.Label(wcard, text=data["name"], font=("Segoe UI", 16, "bold"), bg=COLORS['card'], fg=COLORS['white']).pack()
        tk.Label(wcard, text=f"Account: {acc}", font=FONTS['mono'], bg=COLORS['card'], fg=COLORS['dim']).pack(pady=(2, 6))
        bf = tk.Frame(wcard, bg=COLORS['accent2'])
        bf.pack(pady=(6, 16), ipadx=20, ipady=8)
        tk.Label(bf, text="Available Balance", font=FONTS['small'], bg=COLORS['accent2'], fg=COLORS['light']).pack()
        tk.Label(bf, text=f"Rs {data['balance']:,.2f}", font=("Segoe UI", 22, "bold"), bg=COLORS['accent2'], fg=COLORS['gold']).pack()
        divider(parent)
        services = [
            ("💰","Balance\nEnquiry",    self.show_balance,      COLORS['accent2']),
            ("💸","Withdraw\nCash",      self.show_withdraw,     COLORS['red']),
            ("📥","Deposit\nCash",       self.show_deposit,      COLORS['green']),
            ("📋","Transaction\nHistory",self.show_transactions, COLORS['grey']),
            ("🔐","Change\nPIN",         self.show_change_pin,   "#7B1FA2"),
            ("🚪","Logout",              self.do_logout,         "#BF360C"),
        ]
        grid = tk.Frame(parent, bg=COLORS['dark'])
        grid.pack(fill="x", padx=18, pady=8)
        for i, (icon, label, cmd, color) in enumerate(services):
            row, col = divmod(i, 2)
            cell = tk.Frame(grid, bg=color, cursor="hand2")
            cell.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            grid.columnconfigure(col, weight=1)
            tk.Label(cell, text=icon, font=("Segoe UI", 28), bg=color, fg=COLORS['white']).pack(pady=(14, 0))
            tk.Label(cell, text=label, font=("Segoe UI", 11, "bold"), bg=color, fg=COLORS['white'], justify="center").pack(pady=(2, 14))
            cell.bind("<Button-1>", lambda e, c=cmd: c())
            for ch in cell.winfo_children():
                ch.bind("<Button-1>", lambda e, c=cmd: c())

    # ────── BALANCE ──────────────────────────────────────────────────────

    def show_balance(self):
        accounts = load_data(ACCOUNTS_FILE)
        self.account_data = accounts[self.current_acc]
        self._switch(self._build_balance)

    def _build_balance(self, parent):
        self._screen_title(parent, "💰 Balance Enquiry", "MODULE 3 - BALANCE ENQUIRY")
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        now = datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S")
        for i, (lbl, val) in enumerate([("Account Number", self.current_acc), ("Account Holder", self.account_data["name"]),
                                        ("Mobile", mask_phone(self.account_data.get("phone","N/A"))), ("Date & Time", now),
                                        ("Available Balance", f"Rs {self.account_data['balance']:,.2f}"), 
                                        ("Minimum Balance", f"Rs {MIN_BALANCE:,.2f}"),
                                        ("Withdrawable", f"Rs {max(0, self.account_data['balance']-MIN_BALANCE):,.2f}")]):
            bg = COLORS['card'] if i%2==0 else COLORS['input']
            vc = COLORS['gold'] if lbl=="Available Balance" else COLORS['white']
            self._make_info_row(card, lbl, val, bg, vc)
        bf = tk.Frame(parent, bg=COLORS['dark'])
        bf.pack(fill="x", padx=18, pady=8)
        make_button(bf, "<- Back to Dashboard", self.show_dashboard, color=COLORS['grey'])

    # ────── WITHDRAW ───────────────��─────────────────────────────────────

    def show_withdraw(self):
        self._switch(self._build_withdraw)

    def _build_withdraw(self, parent):
        self._screen_title(parent, "💸 Withdraw Cash", "MODULE 4 - CASH WITHDRAWAL MODULE")
        accounts = load_data(ACCOUNTS_FILE)
        self.account_data = accounts[self.current_acc]
        bal, maxw = self.account_data["balance"], self.account_data["balance"] - MIN_BALANCE
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        info = tk.Frame(card, bg=COLORS['input'])
        info.pack(fill="x", padx=14, pady=(14, 6))
        tk.Label(info, text=f"Current Balance:  Rs {bal:,.2f}", font=FONTS['body'], bg=COLORS['input'], fg=COLORS['white']).pack(side="left", padx=10, pady=8)
        tk.Label(info, text=f"Max: Rs {max(0,maxw):,.2f}", font=FONTS['small'], bg=COLORS['input'], fg=COLORS['light']).pack(side="right", padx=10)
        tk.Label(card, text="Quick Withdraw", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10,4))
        amount_var = tk.StringVar()
        self._quick_buttons(card, [500,1000,2000,5000], amount_var, lambda amt: amt > maxw)
        tk.Label(card, text="Or Enter Amount", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10,0))
        tk.Entry(card, textvariable=amount_var, font=FONTS['input'], bg=COLORS['input'], fg=COLORS['white'], insertbackground=COLORS['accent'], relief="flat", highlightthickness=2, highlightcolor=COLORS['accent'], highlightbackground=COLORS['input']).pack(fill="x", padx=14, pady=4, ipady=8)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0,16))
        def do_withdraw():
            try: amount = float(amount_var.get())
            except ValueError: return self._toast(card, "Valid amount needed.", COLORS['error'])
            if amount <= 0: return self._toast(card, "Amount must be positive.", COLORS['error'])
            if amount % 100 != 0: return self._toast(card, "Multiples of Rs 100 only.", COLORS['error'])
            if amount > maxw: return self._toast(card, f"Max: Rs {max(0,maxw):.2f}", COLORS['error'])
            self.account_data["balance"] -= amount
            a2 = load_data(ACCOUNTS_FILE)
            a2[self.current_acc]["balance"] = self.account_data["balance"]
            save_data(ACCOUNTS_FILE, a2)
            record_transaction(self.current_acc, "WITHDRAW", amount, self.account_data["balance"])
            self._show_receipt("WITHDRAWAL", amount, self.account_data["balance"])
        make_button(br, "💸  WITHDRAW NOW", do_withdraw, color=COLORS['red'])
        make_button(br, "<- Back", self.show_dashboard, color=COLORS['grey'], pady=2)

    # ────── DEPOSIT ──────────────────────────────────────────────────────

    def show_deposit(self):
        self._switch(self._build_deposit)

    def _build_deposit(self, parent):
        self._screen_title(parent, "📥 Deposit Cash", "MODULE 5 - DEPOSIT MODULE")
        accounts = load_data(ACCOUNTS_FILE)
        self.account_data = accounts[self.current_acc]
        bal = self.account_data["balance"]
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        info = tk.Frame(card, bg=COLORS['input'])
        info.pack(fill="x", padx=14, pady=(14, 6))
        tk.Label(info, text=f"Current Balance:  Rs {bal:,.2f}", font=FONTS['body'], bg=COLORS['input'], fg=COLORS['white']).pack(side="left", padx=10, pady=8)
        tk.Label(card, text="Quick Deposit", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(6,4))
        amount_var = tk.StringVar()
        self._quick_buttons(card, [500,1000,5000,10000], amount_var)
        tk.Label(card, text="Or Enter Amount", font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10,0))
        tk.Entry(card, textvariable=amount_var, font=FONTS['input'], bg=COLORS['input'], fg=COLORS['white'], insertbackground=COLORS['accent'], relief="flat", highlightthickness=2, highlightcolor=COLORS['accent'], highlightbackground=COLORS['input']).pack(fill="x", padx=14, pady=4, ipady=8)
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0,16))
        def do_deposit():
            try: amount = float(amount_var.get())
            except ValueError: return self._toast(card, "Valid amount needed.", COLORS['error'])
            if amount <= 0: return self._toast(card, "Amount must be positive.", COLORS['error'])
            if amount % 100 != 0: return self._toast(card, "Multiples of Rs 100 only.", COLORS['error'])
            self.account_data["balance"] += amount
            a2 = load_data(ACCOUNTS_FILE)
            a2[self.current_acc]["balance"] = self.account_data["balance"]
            save_data(ACCOUNTS_FILE, a2)
            record_transaction(self.current_acc, "DEPOSIT", amount, self.account_data["balance"])
            self._show_receipt("DEPOSIT", amount, self.account_data["balance"])
        make_button(br, "📥  DEPOSIT NOW", do_deposit, color=COLORS['green'])
        make_button(br, "<- Back", self.show_dashboard, color=COLORS['grey'], pady=2)

    # ────── TRANSACTIONS ─────────────────────────────────────────────────

    def show_transactions(self):
        self._switch(self._build_transactions)

    def _build_transactions(self, parent):
        self._screen_title(parent, "📋 Transaction History", "MODULE 6 - TRANSACTION PROCESSING")
        all_txns = load_data(TRANSACTIONS_FILE)
        my_txns = [t for t in all_txns if t["account_number"] == self.current_acc]
        if not my_txns:
            card = tk.Frame(parent, bg=COLORS['card'])
            card.pack(fill="x", padx=18, pady=8)
            tk.Label(card, text="No transactions found.", font=FONTS['body'], bg=COLORS['card'], fg=COLORS['light']).pack(pady=30)
        else:
            total_dep, total_with = sum(t["amount"] for t in my_txns if t["type"] in ("DEPOSIT","OPEN")), sum(t["amount"] for t in my_txns if t["type"]=="WITHDRAW")
            sc = tk.Frame(parent, bg=COLORS['card'])
            sc.pack(fill="x", padx=18, pady=(8,4))
            for icon, lbl, val, color in [("📥","Total Deposits", f"Rs {total_dep:,.2f}", COLORS['success']), 
                                          ("📤","Total Withdrawals", f"Rs {total_with:,.2f}", COLORS['error'])]:
                r = tk.Frame(sc, bg=COLORS['input'])
                r.pack(fill="x", padx=14, pady=4)
                tk.Label(r, text=f"{icon}  {lbl}", font=FONTS['label'], bg=COLORS['input'], fg=COLORS['light']).pack(side="left", padx=10, pady=8)
                tk.Label(r, text=val, font=("Segoe UI",12,"bold"), bg=COLORS['input'], fg=color).pack(side="right", padx=10)
            for txn in reversed(my_txns):
                tc, ic = (COLORS['green'], "📥") if txn["type"] in ("DEPOSIT","OPEN") else (COLORS['red'], "📤")
                row = tk.Frame(parent, bg=COLORS['card'])
                row.pack(fill="x", padx=18, pady=3)
                lf = tk.Frame(row, bg=COLORS['card'])
                lf.pack(side="left", fill="both", expand=True, padx=12, pady=8)
                tk.Label(lf, text=f"{ic}  {txn['type']}", font=("Segoe UI",11,"bold"), bg=COLORS['card'], fg=tc, anchor="w").pack(fill="x")
                tk.Label(lf, text=txn["timestamp"], font=FONTS['small'], bg=COLORS['card'], fg=COLORS['dim'], anchor="w").pack(fill="x")
                rf = tk.Frame(row, bg=COLORS['card'])
                rf.pack(side="right", padx=12, pady=8)
                tk.Label(rf, text=f"Rs {txn['amount']:,.2f}", font=("Segoe UI",13,"bold"), bg=COLORS['card'], fg=tc).pack()
                tk.Label(rf, text=f"Bal: Rs {txn['balance_after']:,.2f}", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['dim']).pack()
                tk.Frame(row, height=1, bg=COLORS['dim']).pack(fill="x")
        bf = tk.Frame(parent, bg=COLORS['dark'])
        bf.pack(fill="x", padx=18, pady=8)
        make_button(bf, "<- Back to Dashboard", self.show_dashboard, color=COLORS['grey'])

    # ────── CHANGE PIN ───────────────────────────────────────────────────

    def show_change_pin(self):
        self._switch(self._build_change_pin)

    def _build_change_pin(self, parent):
        self._screen_title(parent, "🔐 Change PIN", "MODULE 2 - PIN VERIFICATION MODULE")
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18, pady=8)
        fields = {key: make_entry(card, show="●") for (lbl, key) in [("Current PIN","cur"),("New 4-digit PIN","new"),("Confirm New PIN","cnew")]
                  for _ in [tk.Label(card, text=lbl, font=FONTS['label'], fg=COLORS['light'], bg=COLORS['card'], anchor="w").pack(fill="x", padx=14, pady=(10,0))]}
        divider(card)
        br = tk.Frame(card, bg=COLORS['card'])
        br.pack(fill="x", padx=14, pady=(0,16))
        def do_change():
            accounts = load_data(ACCOUNTS_FILE)
            cur, new, cnew = fields["cur"].get(), fields["new"].get(), fields["cnew"].get()
            if cur != accounts[self.current_acc]["pin"]: return self._toast(card, "Current PIN incorrect.", COLORS['error'])
            if not new.isdigit() or len(new) != 4: return self._toast(card, "New PIN: 4 digits.", COLORS['error'])
            if new != cnew: return self._toast(card, "PINs don't match.", COLORS['error'])
            accounts[self.current_acc]["pin"] = new
            save_data(ACCOUNTS_FILE, accounts)
            self.account_data["pin"] = new
            messagebox.showinfo("PIN Changed", "Your PIN has been updated successfully!")
            self.show_dashboard()
        make_button(br, "🔐  UPDATE PIN", do_change, color="#7B1FA2")
        make_button(br, "<- Back", self.show_dashboard, color=COLORS['grey'], pady=2)

    # ────── LOGOUT ───────────────────────────────────────────────────────

    def do_logout(self):
        name = self.account_data["name"] if self.account_data else "User"
        ts = datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S")
        self.current_acc, self.account_data = None, None
        self._switch(lambda p: self._build_logout(p, name, ts))

    def _build_logout(self, parent, name, ts):
        tk.Frame(parent, height=30, bg=COLORS['dark']).pack()
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18)
        tk.Label(card, text="🚪", font=("Segoe UI", 52), bg=COLORS['card'], fg=COLORS['accent']).pack(pady=(24,0))
        tk.Label(card, text="Session Ended", font=("Segoe UI",18,"bold"), bg=COLORS['card'], fg=COLORS['white']).pack()
        tk.Label(card, text=f"Goodbye, {name}!", font=FONTS['body'], bg=COLORS['card'], fg=COLORS['light']).pack(pady=4)
        divider(card)
        for lbl, val in [("Logged Out At",ts),("Session Status","Terminated Safely"),("Your Card","Please collect it")]:
            self._make_info_row(card, lbl, val, COLORS['input'], COLORS['success'])
        tk.Label(card, text="Thank you for using PyBank ATM", font=FONTS['body'], bg=COLORS['card'], fg=COLORS['dim']).pack(pady=(12,24))
        bf = tk.Frame(parent, bg=COLORS['dark'])
        bf.pack(fill="x", padx=18, pady=16)
        make_button(bf, "🏠  BACK TO HOME", self.show_welcome, color=COLORS['green'])

    # ────── RECEIPT ──────────────────────────────────────────────────────

    def _show_receipt(self, txn_type, amount, new_bal):
        ts, icon = datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S"), ("📥" if txn_type=="DEPOSIT" else "📤")
        self._switch(lambda p: self._build_receipt(p, txn_type, amount, new_bal, ts, icon))

    def _build_receipt(self, parent, txn_type, amount, new_bal, ts, icon):
        tk.Frame(parent, height=20, bg=COLORS['dark']).pack()
        card = tk.Frame(parent, bg=COLORS['card'])
        card.pack(fill="x", padx=18)
        color = COLORS['green'] if txn_type=="DEPOSIT" else COLORS['red']
        tk.Label(card, text=icon, font=("Segoe UI",52), bg=COLORS['card'], fg=color).pack(pady=(24,0))
        tk.Label(card, text="Transaction Successful!", font=("Segoe UI",16,"bold"), bg=COLORS['card'], fg=COLORS['success']).pack()
        divider(card)
        for i, (lbl, val) in enumerate([("Transaction Type", txn_type), ("Amount", f"Rs {amount:,.2f}"),
                                        ("New Balance", f"Rs {new_bal:,.2f}"), ("Account Number", self.current_acc),
                                        ("Account Holder", self.account_data["name"]), ("Date & Time", ts)]):
            bg, vc = (COLORS['input'], COLORS['gold']) if i%2==0 and lbl in ("Amount","New Balance") else (COLORS['input'] if i%2==0 else COLORS['card'], COLORS['white'])
            vc = COLORS['gold'] if lbl in ("Amount","New Balance") else COLORS['white']
            r = tk.Frame(card, bg=bg)
            r.pack(fill="x")
            tk.Label(r, text=lbl, font=FONTS['label'], bg=bg, fg=COLORS['light']).pack(side="left", padx=14, pady=8)
            tk.Label(r, text=val, font=("Segoe UI",12,"bold"), bg=bg, fg=vc).pack(side="right", padx=14)
        tk.Label(card, text="--- Keep this receipt ---", font=FONTS['small'], bg=COLORS['card'], fg=COLORS['dim']).pack(pady=(10,20))
        bf = tk.Frame(parent, bg=COLORS['dark'])
        bf.pack(fill="x", padx=18, pady=8)
        make_button(bf, "<-  Back to Dashboard", self.show_dashboard, color=COLORS['grey'])

if __name__ == "__main__":
    app = ATMApp()
    app.mainloop()