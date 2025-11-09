# Custom Domain Setup Guide: unitest.in

This guide will help you set up the custom domain `unitest.in` for your Vercel deployment.

## Prerequisites

1. **Domain Ownership**: You must own the domain `unitest.in`
2. **Domain Registrar Access**: Access to your domain registrar (where you bought the domain)
3. **Vercel Account**: Your project must be deployed on Vercel

## Step 1: Add Domain to Vercel

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your project (`UNITEST-EXAM` or your project name)
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `unitest.in`
6. Click **Add**

## Step 2: Configure DNS Records

Vercel will show you the DNS records you need to add. You have two options:

### Option A: Use Vercel Nameservers (Recommended)

1. In Vercel, you'll see nameservers like:
   - `ns1.vercel-dns.com`
   - `ns2.vercel-dns.com`
2. Go to your domain registrar (where you bought `unitest.in`)
3. Find **DNS Settings** or **Nameservers**
4. Replace the current nameservers with Vercel's nameservers
5. Save and wait 24-48 hours for propagation

### Option B: Add A/CNAME Records (Alternative)

If you can't change nameservers, add these DNS records:

**For Root Domain (unitest.in):**
- Type: `A`
- Name: `@` or leave blank
- Value: `76.76.21.21` (Vercel's IP - check Vercel dashboard for current IP)

**For WWW Subdomain (www.unitest.in):**
- Type: `CNAME`
- Name: `www`
- Value: `cname.vercel-dns.com` (or the value shown in Vercel dashboard)

## Step 3: Verify Domain

1. After adding DNS records, go back to Vercel
2. Click **Refresh** or **Verify** next to your domain
3. Wait for verification (can take a few minutes to 24 hours)
4. Once verified, you'll see a green checkmark ✅

## Step 4: SSL Certificate (Automatic)

- Vercel automatically provisions SSL certificates via Let's Encrypt
- This usually happens within minutes after domain verification
- Your site will be accessible at `https://unitest.in`

## Step 5: Update Google Search Console

1. Go to [Google Search Console](https://search.google.com/search-console)
2. **Remove** the old property: `unitest-ai-exam-platform.vercel.app`
3. **Add Property** → Enter: `unitest.in`
4. Choose verification method:
   - **HTML file**: Download the verification file
   - **HTML tag**: Copy the meta tag
   - **DNS**: Add TXT record (if you have DNS access)
5. After verification, submit your sitemap: `https://unitest.in/sitemap.xml`

## Step 6: Test Your Domain

After DNS propagation (24-48 hours), test:

1. **Visit**: `https://unitest.in` - Should load your site
2. **Visit**: `https://unitest.in/sitemap.xml` - Should show XML
3. **Visit**: `https://unitest.in/robots.txt` - Should show robots.txt

## Troubleshooting

### Domain Not Resolving

- **Wait**: DNS changes can take 24-48 hours to propagate globally
- **Check DNS**: Use `nslookup unitest.in` or `dig unitest.in` to verify
- **Clear Cache**: Clear browser cache or use incognito mode

### SSL Certificate Issues

- Vercel automatically provisions SSL, but it can take up to 24 hours
- If still not working after 24 hours, contact Vercel support

### Vercel Shows "Invalid Configuration"

- Double-check DNS records match exactly what Vercel shows
- Ensure nameservers are correctly set if using Option A
- Wait for DNS propagation (can take time)

## Important Notes

✅ **All code has been updated** - All URLs in the codebase now use `unitest.in`
✅ **Sitemap updated** - Sitemap now points to `unitest.in`
✅ **Meta tags updated** - All SEO tags now use `unitest.in`
✅ **Robots.txt updated** - Robots.txt now references `unitest.in`

## After Setup

Once `unitest.in` is live:

1. **Test all pages** to ensure they work
2. **Submit sitemap** to Google Search Console: `https://unitest.in/sitemap.xml`
3. **Monitor** Google Search Console for indexing status
4. **Update any external links** that point to the old domain

---

**Need Help?** Check Vercel's documentation: https://vercel.com/docs/concepts/projects/domains

