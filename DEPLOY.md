# 🚀 Grace Ville – Free Vercel Deployment Guide

Deploy the **Grace Ville** Django web application to **Vercel** for 100% free hosting with a live database, real-time SMTP email notifications, WhatsApp concierge booking, and persistent cloud storage.

---

## 📌 Architecture & Features Included

1. **Free Vercel Serverless Hosting**: Zero credit card required on Vercel's Hobby Tier.
2. **Live SQLite Database**: Pre-seeded `db.sqlite3` is automatically copied to `/tmp/db.sqlite3` on lambda startup, enabling live reads and writes without read-only filesystem crashes.
3. **Permanent Cloud Booking Storage (MongoDB Atlas)**:
   - Every booking inquiry and contact message is saved to MongoDB Atlas free M0 cluster (512 MB forever free) if `MONGODB_URI` is provided.
   - Even when serverless lambdas recycle, your guest bookings are never lost!
4. **Custom Receiver Email (SMTP)**:
   - When any guest submits a booking or contact message, an instant notification email is dispatched to your custom receiver email (`NOTIFICATION_RECEIVER_EMAIL`, e.g. `xyz@gmail.com`).
   - Guest receives an automated confirmation email.
5. **WhatsApp Concierge Booking**:
   - Dynamic WhatsApp integration with pre-filled booking details (`Ref ID`, `Name`, `Phone`, `Stay Package`).
5. **Online Appointment & Visit Booking Feature**:
   - Universal **"Schedule a Visit"** modal accessible from the navbar on every single page.
   - Visitors can schedule a **Villa Pre-Visit / Site Inspection**, Overnight Stay, Day Outing, or Family Celebration.
   - Pick preferred date (`type="date"`), timing slot (Morning, Afternoon, Full Day, Overnight), and guest count.
   - Instant SQLite database save + real-time email to host + one-click WhatsApp chat verification.
6. **WhatsApp Concierge Booking**:
   - Dynamic WhatsApp integration with pre-filled booking details (`Ref ID`, `Name`, `Phone`, `Package`, `Date`, `Slot`).
   - Floating WhatsApp button on every page.
6. **WhiteNoise Static Serving**:
7. **WhiteNoise Static Serving**:
   - High-resolution villa images, stylesheets, and scripts served with compression and caching.

---

## 📁 Which Directory is Your Git Root?

**YOUR GIT ROOT IS `E:\New folder\app`!**

- You MUST run `git init` inside `E:\New folder\app` (NOT the parent folder).
- **Why?** Because `app/` is the self-contained Django project containing `manage.py`, `vercel.json`, `requirements.txt`, and `db.sqlite3`.
- **On Vercel**: Setting the root to `app` means Vercel's **Root Directory** setting is simply `./` (default). You don't have to upload 500 MB of raw unedited DSLR photos or downloaded zips from the parent directory.

---

## 🛠️ Step 1: Configure Your Environment Variables (`.env`)

In the `app/` folder, inspect or create your `.env` file (or prepare these for Vercel's Dashboard):

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Random Django secret key | `django-insecure-xnoqfbwn...` (or generate new) |
| `DEBUG` | Debug mode (`False` in production) | `False` |
| `ALLOWED_HOSTS` | Allowed host domains | `.vercel.app,localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for form POSTs | `https://*.vercel.app` |
| `WHATSAPP_PHONE` | Host WhatsApp number without `+` | `917768956163` |
| `OWNER_PHONE` | Owner direct contact number without `+` | `919699825732` |
| `NOTIFICATION_RECEIVER_EMAIL` | **Where to send booking alerts** (can be comma-separated) | `graceville1911@gmail.com,nikhilchandurkar24@gmail.com` |
| `EMAIL_BACKEND` | Django email backend | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` |
| `EMAIL_HOST_USER` | Sending email address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | 16-character Gmail App Password | `xxxx xxxx xxxx xxxx` |
| `DEFAULT_FROM_EMAIL` | Sender name and email | `Grace Ville <your-email@gmail.com>` |
| `MONGODB_URI` *(Optional)* | Free MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster0...` |
| `DATABASE_URL` *(Optional)* | Free PostgreSQL (Neon/Supabase) | `postgresql://user:pass@ep-...neon.tech/neondb` |

> 💡 **Tip for Gmail SMTP**:
> 1. Go to your Google Account: [myaccount.google.com/security](https://myaccount.google.com/security)
> 2. Enable **2-Step Verification**.
> 3. Search for **"App Passwords"** ([myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
> 4. Create an App Password named "Grace Ville Website" and copy the 16-character code into `EMAIL_HOST_PASSWORD`.

---

## 🗄️ Step 2: (Recommended) Free MongoDB Atlas for Forever-Persistent Bookings

On Vercel serverless, SQLite runs in `/tmp` (which is fast and free, but resets when idle). To keep a permanent, cloud-backed record of every single guest booking:

1. Create a free account at [mongodb.com/atlas](https://www.mongodb.com/atlas).
2. Create a free **M0 Sandbox Cluster** (select AWS, nearest region like Mumbai `ap-south-1`).
3. Under **Database Access**, create a user (e.g. `graceville_admin` and password).
4. Under **Network Access**, add IP Address `0.0.0.0/0` (Allow Access from Anywhere).
5. Click **Connect** -> **Drivers (Python)** -> Copy the connection string:
   ```text
   mongodb+srv://graceville_admin:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   ```
6. Set this as `MONGODB_URI` in your `.env` or Vercel Environment Variables. All inquiries will automatically stream to MongoDB Atlas!

---

## 📦 Step 3: Push Your Code to GitHub

Open PowerShell in `E:\New folder\app`:

```powershell
cd "E:\New folder\app"

# 1. Initialize git (if not already done)
git init

# 2. Stage all files (excluding virtualenv and secrets via .gitignore)
git add .

# 3. Commit the project
git commit -m "Grace Ville full-stack Django site with Vercel deployment and WhatsApp booking"
git commit -m "Grace Ville full-stack Django site with appointment booking, Vercel deployment, and WhatsApp"

# 4. Create main branch
git branch -M main

# 5. Link your GitHub repository (create a repository on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/graceville-villa.git

# 6. Push to GitHub
git push -u origin main
```

---

## 🌐 Step 4: Deploy on Vercel

1. Log into [vercel.com](https://vercel.com) (free signup with GitHub).
2. Click **"Add New..."** -> **"Project"**.
3. Import your **`graceville-villa`** repository.
4. In the Project Configuration screen:
   - **Framework Preset**: **Django** (auto-detected)
   - **Root Directory**: Leave as `./` (default).
5. Expand the **Environment Variables** section and add the keys from your `.env`:
   - `SECRET_KEY`: *(paste your secret key)*
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.vercel.app`
   - `NOTIFICATION_RECEIVER_EMAIL`: `graceville1911@gmail.com,nikhilchandurkar24@gmail.com`
   - `WHATSAPP_PHONE`: `917768956163`
   - `OWNER_PHONE`: `919699825732`
   - `EMAIL_BACKEND`: `django.core.mail.backends.smtp.EmailBackend`
   - `EMAIL_HOST`: `smtp.gmail.com`
   - `EMAIL_PORT`: `587`
   - `EMAIL_USE_TLS`: `True`
   - `EMAIL_HOST_USER`: `nikhilchandurkar24@gmail.com`
   - `EMAIL_HOST_PASSWORD`: `rhlavdkyccvnutgt`
   - `DEFAULT_FROM_EMAIL`: `Grace Ville Reservations <nikhilchandurkar24@gmail.com>`
   - `MONGODB_URI`: *(your MongoDB Atlas URI from Step 2)*
6. Click **Deploy**!
7. In ~60 seconds, Vercel will build your static files and deploy your live URL (e.g. `https://graceville-villa.vercel.app`).

---

## ✅ Step 5: Verify Live Features

Once deployed, visit your live Vercel URL:

1. **Homepage & Navbar**: Verify the logo *"Grace Ville"* is on a single line and responsive.
2. **Floating WhatsApp Widget**: Click the floating button in the bottom right corner — it opens WhatsApp chat directly with Grace Ville.
3. **Submit a Booking**:
   - Go to Contact page or click *Instant WhatsApp Booking*.
   - Fill in Name, Phone, Stay Type, and Dates.
   - Click *Submit Booking Inquiry*:
     - An instant reference code is displayed (`GV-XXXXXX`).
     - A direct WhatsApp button pops up to confirm details on WhatsApp.
     - An email notification is sent to `NOTIFICATION_RECEIVER_EMAIL`.
     - A copy is stored in MongoDB Atlas (and local SQLite).
4. **Staff Admin Portal**:
   - Go to `https://your-domain.vercel.app/admin/`
   - Login: `admin` / `admin123`
   - Review inquiries, filter by status, and update notes.

---

## ❓ Frequently Asked Questions (FAQ)

### Q: Why did the database reset on Vercel after a while?
Vercel is serverless; lambdas sleep after inactivity and `/tmp` is wiped. That's why we added **MongoDB Atlas** integration! Simply set `MONGODB_URI` in Vercel environment variables, and every inquiry will be saved in MongoDB Atlas forever, 100% free.

### Q: Can I use my own custom domain (e.g., graceville.in)?
Yes! In Vercel Project Settings -> **Domains**, add `graceville.in`. Add `graceville.in,www.graceville.in` to `ALLOWED_HOSTS` and `https://graceville.in` to `CSRF_TRUSTED_ORIGINS`.

### Q: How do I test email locally before deploying?
Keep `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in your local `app/.env`. Whenever a booking is made, Django will print the full email in your terminal instead of sending an actual SMTP message.

