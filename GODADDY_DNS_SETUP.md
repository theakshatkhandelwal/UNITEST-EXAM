# GoDaddy DNS Setup Guide for unitest.in

This guide will help you configure your `unitest.in` domain purchased from GoDaddy to work with Vercel.

## Step 1: Add Domain to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project (`UNITEST-EXAM` or your project name)
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `unitest.in`
6. Click **Add**
7. Also add: `www.unitest.in` (click Add Domain again)

## Step 2: Get DNS Records from Vercel

After adding the domain, Vercel will show you DNS configuration. You'll see:

**For Root Domain (unitest.in):**
- Type: `A`
- Name: `@` (or blank)
- Value: An IP address (e.g., `76.76.21.21` or `216.198.79.1` - Vercel will show the current one)

**For WWW Subdomain (www.unitest.in):**
- Type: `CNAME`
- Name: `www`
- Value: `cname.vercel-dns.com` (or similar - Vercel will show the exact value)

**OR Vercel Nameservers:**
- `ns1.vercel-dns.com`
- `ns2.vercel-dns.com`

## Step 3: Configure DNS in GoDaddy

### Option A: Use Vercel Nameservers (EASIEST - Recommended)

1. Log in to [GoDaddy](https://www.godaddy.com)
2. Go to **My Products** → Click **DNS** next to `unitest.in`
3. Scroll down to **Nameservers** section
4. Click **Change**
5. Select **Custom** (not "Default")
6. Delete the existing nameservers
7. Add Vercel's nameservers:
   - `ns1.vercel-dns.com`
   - `ns2.vercel-dns.com`
8. Click **Save**
9. Wait 24-48 hours for propagation

### Option B: Add A/CNAME Records (If you can't change nameservers)

1. Log in to [GoDaddy](https://www.godaddy.com)
2. Go to **My Products** → Click **DNS** next to `unitest.in`
3. Scroll to **Records** section

**Add A Record for Root Domain:**
1. Click **Add** button
2. Type: `A`
3. Name: `@` (or leave blank)
4. Value: Enter the IP address from Vercel (e.g., `76.76.21.21` or `216.198.79.1`)
5. TTL: `600` (or default)
6. Click **Save**

**Add CNAME Record for WWW:**
1. Click **Add** button again
2. Type: `CNAME`
3. Name: `www`
4. Value: `cname.vercel-dns.com` (or the value shown in Vercel)
5. TTL: `600` (or default)
6. Click **Save**

**Remove Conflicting Records:**
- If there are any existing A or CNAME records for `@` or `www`, delete them first

## Step 4: Verify in Vercel

1. Go back to Vercel Dashboard → Your Project → Settings → Domains
2. Click **Refresh** next to `unitest.in`
3. Wait for verification (can take a few minutes to 24 hours)
4. Once verified, you'll see a green checkmark ✅
5. SSL certificate will be automatically provisioned (takes a few minutes)

## Step 5: Test Your Domain

After DNS propagation (24-48 hours), test:

1. **Visit**: `https://unitest.in` - Should load your site
2. **Visit**: `https://www.unitest.in` - Should also work
3. **Visit**: `https://unitest.in/sitemap.xml` - Should show XML
4. **Visit**: `https://unitest.in/robots.txt` - Should show robots.txt

## Troubleshooting

### Domain Not Resolving

- **Wait**: DNS changes can take 24-48 hours to propagate globally
- **Check DNS**: 
  - Windows: Open Command Prompt, type `nslookup unitest.in`
  - Mac/Linux: Open Terminal, type `dig unitest.in`
- **Clear Cache**: Clear browser cache or use incognito mode
- **Check GoDaddy**: Make sure records are saved correctly

### Vercel Shows "Invalid Configuration"

- Double-check DNS records match exactly what Vercel shows
- Ensure there are no typos in IP addresses or CNAME values
- Wait for DNS propagation (can take up to 48 hours)
- Try clicking "Refresh" in Vercel again

### SSL Certificate Not Working

- Vercel automatically provisions SSL, but it can take up to 24 hours after domain verification
- Make sure domain is verified in Vercel first
- If still not working after 24 hours, contact Vercel support

### GoDaddy DNS Settings Not Saving

- Make sure you're logged into the correct GoDaddy account
- Check if domain is locked (unlock it in domain settings)
- Try refreshing the page and saving again

## Important Notes

✅ **All code has been updated** - All URLs now use `unitest.in`
✅ **Sitemap updated** - Points to `https://unitest.in/sitemap.xml`
✅ **Robots.txt updated** - References `https://unitest.in`
✅ **Meta tags updated** - All SEO tags use `unitest.in`

## Next Steps After Domain is Live

1. **Update Google Search Console**:
   - Remove old property: `unitest-ai-exam-platform.vercel.app`
   - Add new property: `unitest.in`
   - Verify ownership
   - Submit sitemap: `https://unitest.in/sitemap.xml`

2. **Test Everything**:
   - All pages load correctly
   - Sitemap is accessible
   - Robots.txt is accessible
   - SSL certificate is working (HTTPS)

3. **Monitor**:
   - Check Vercel dashboard for any errors
   - Monitor Google Search Console for indexing

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs/concepts/projects/domains
- GoDaddy Support: https://www.godaddy.com/help
- Check DNS propagation: https://www.whatsmydns.net/


