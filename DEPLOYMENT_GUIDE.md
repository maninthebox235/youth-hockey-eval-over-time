# Streamlit Cloud Deployment Guide

This guide will help you deploy the Youth Hockey Tracker app to Streamlit Cloud.

## Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://share.streamlit.io/)
- Supabase database already set up ✅

## Step 1: Prepare for Deployment

The app is already configured and ready to deploy:
- ✅ Configuration fixes committed (.streamlit/config.toml, database/config.py)
- ✅ Supabase database created with all tables
- ✅ Test data migrated (testcoach user, Lightning 10U team, 5 players, sample evaluation)
- ✅ Branch: `devin/1760363940-game-evaluation`

## Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app" button
   - Select repository: `YouthHockeyTracker`
   - Select branch: `devin/1760363940-game-evaluation`
   - Main file path: `main.py`

3. **Configure Secrets**
   - Click "Advanced settings"
   - In the "Secrets" section, add your Supabase DATABASE_URL:
     ```toml
     DATABASE_URL = "your-supabase-connection-string"
     ```
   - Get your connection string from Supabase dashboard
   - Format: `postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres`

4. **Deploy**
   - Click "Deploy!" button
   - Wait 2-3 minutes for deployment to complete
   - Streamlit will provide a public URL (format: `https://your-app-name.streamlit.app`)

## Step 3: Test the Deployed App

1. **Access the App**
   - Navigate to your deployed URL
   - Verify the landing page loads without errors

2. **Test Login**
   - Click "LOGIN" button
   - Username: `testcoach`
   - Password: `password123`
   - Click "Login"

3. **Test Game Evaluation Feature**
   - After login, go to "Team Management" in sidebar
   - Select "Game Evaluation"
   - Choose "Lightning 10U (U10)" team
   - Go to "View History" tab
   - Verify sample evaluation is displayed (vs Thunder Hockey Club, W 4-2)

## Expected Results

✅ **No JavaScript/React errors** - Configuration fixes eliminated:
- "Custom element already defined" error
- "Minified React error #321"
- "NotFoundError: Failed to execute 'removeChild'"

✅ **App loads cleanly** - No "Database tables created successfully" spam

✅ **Test data accessible** - Sample evaluation visible in Game Evaluation feature

## Troubleshooting

**If deployment fails:**
- Check that the DATABASE_URL secret is correctly formatted
- Verify the branch name is correct: `devin/1760363940-game-evaluation`
- Check Streamlit Cloud logs for specific error messages

**If app loads but shows database errors:**
- Verify DATABASE_URL secret is set in Streamlit Cloud
- Check Supabase database is accessible (no IP restrictions)

**If login doesn't work:**
- Verify DATABASE_URL is correct and database has test data
- Check Streamlit Cloud logs for authentication errors

## Test Data Summary

**User:**
- Username: `testcoach`
- Password: `password123`
- Name: Test Coach

**Team:**
- Name: Lightning 10U
- Age Group: U10

**Players (5):**
- Jake Thompson (Forward, Age 9)
- Emma Martinez (Defense, Age 10)
- Liam Johnson (Forward, Age 9)
- Sophia Chen (Goalie, Age 10)
- Noah Williams (Defense, Age 9)

**Sample Evaluation:**
- Opponent: Thunder Hockey Club
- Date: 2025-10-13
- Score: W 4-2
- Location: Home
- Ratings: Spacing 4/5, Forechecking 3/5, Backchecking 3/5, Breakout 3/5

## Next Steps After Deployment

1. Share the deployed URL with your team
2. Create additional teams and players
3. Add more game evaluations
4. Customize the app for your specific needs

## Support

If you encounter issues during deployment, check:
- Streamlit Cloud documentation: https://docs.streamlit.io/streamlit-community-cloud
- Supabase documentation: https://supabase.com/docs
