# 🏡 Grace Ville – Luxury Private Villa & Nature Sanctuary

> **Relax, Celebrate & Reconnect with Nature**  
> Located in picturesque Udachiwadi, Saswad, just 33 km from Pune City near the proposed Purandar Airport.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)
[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas_Free_M0-brightgreen.svg)](https://www.mongodb.com/atlas)

---

## 🌟 Property Highlights & Amenities

- 🛏️ **Accommodations**: 3 Air-Conditioned Bedrooms + 1 Air-Conditioned Dormitory
- 🚿 **Bathrooms**: 5 Designer Washrooms with rain showers
- 🍳 **Kitchens**: 3 Fully-Equipped Kitchens (cooktops, refrigeration, prep areas)
- 🏊 **Swimming Pool**: Private pool featuring a cascading natural stone waterfall
- 🎵 **Entertainment**: High-bass JBL party sound system
- 🌅 **Sky Terraces**: 360° panoramic view of Purandar mountains and sunset horizon
- 🌳 **Nature Trails**: Direct access to hill trekking and lush fruit orchards (mango & jamun)
- 🚗 **Parking**: Ample secure private parking on premises

---

## ⚡ Web Application Features

1. **Online Appointment & Visit Booking**:
   - Universal **"Schedule a Visit"** popup modal accessible on all pages.
   - Visitors can schedule pre-visits / site inspections, overnight stays, or day outings.
   - Date picker, time slot selection (Morning, Afternoon, Full Day), and guest count.
2. **Instant WhatsApp Concierge**:
   - Deep-linked one-click WhatsApp reservation with auto-generated booking reference IDs (`GV-XXXXXX`).
   - Floating WhatsApp widget available on all screen sizes.
3. **Dual Persistence Engine**:
   - **Local / Serverless Database**: SQLite with auto-cloning to `/tmp/db.sqlite3` on Vercel.
   - **Permanent Cloud Sync**: Automatic mirroring of all booking inquiries and contact messages to **MongoDB Atlas (Free M0 Cluster)**.
4. **Real-Time SMTP Email Alerts**:
   - Dispatches instant email notifications to staff/management upon every booking or contact submission.
   - Automated confirmation emails sent to visitors.
5. **SEO & Discoverability**:
   - Schema.org `Resort` structured data (Google Rich Results).
   - Social meta tags (OpenGraph & Twitter Cards).
   - Native `/robots.txt` and `/sitemap.xml` routes.

---

## 📞 Direct Contacts

- **Concierge & WhatsApp Reservations**: [+91 77689 56163](tel:+917768956163)
- **Villa Owner Direct**: [+91 96998 25732](tel:+919699825732)
- **Email**: [reservations@graceville.in](mailto:reservations@graceville.in)
- **Address**: Udachiwadi, Saswad, Pune, Maharashtra 412301
- **Google Maps**: [Location Pin](https://maps.app.goo.gl/Udachiwadi)

---

## 🚀 Quick Start (Local Development)

```powershell
# 1. Navigate to app folder
cd app

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run development server
python manage.py runserver 8000
```

- Homepage: [http://localhost:8000/](http://localhost:8000/)
- Admin Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/) (Login: `admin` / `admin123`)

---

## 🌐 Deploy to Vercel (100% Free)

Detailed step-by-step instructions are available in [DEPLOY.md](DEPLOY.md).

```powershell
# Push to your GitHub repository from inside the app directory:
cd app
git init
git add .
git commit -m "Grace Ville full-stack Django site ready for Vercel"
git branch -M main
git remote add origin https://github.com/nikhilchandurkar/graceville.git
git push -u origin main
```

In [Vercel Dashboard](https://vercel.com):
1. Import `nikhilchandurkar/graceville`.
2. Add the environment variables from `.env.example`.
3. Click **Deploy**!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Curated architectural and estate photography © Grace Ville.
Web layout adapted from TemplateMo Villa Agency.

