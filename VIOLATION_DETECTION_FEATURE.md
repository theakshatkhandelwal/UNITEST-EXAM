# Violation Detection Feature

## Overview
This feature adds detection for keyboard shortcuts that indicate potential cheating during quiz taking:
- **Alt+Tab** - Switching between windows/applications
- **Win+Shift+S** - Windows Snipping Tool (screenshot)
- **Win+PrintScreen** - Windows screenshot shortcut
- **PrintScreen** - Standalone screenshot key

## Implementation Details

### Frontend (JavaScript)
- Added keyboard event listeners in `templates/take_shared_quiz.html`
- Detects the prohibited shortcuts and flags them immediately
- Automatically exits quiz and logs violation when detected

### Backend (Python/Flask)
- Added 4 new database columns to `QuizSubmission` model:
  - `alt_tab_flag` (Boolean)
  - `win_shift_s_flag` (Boolean)
  - `win_prtscn_flag` (Boolean)
  - `prtscn_flag` (Boolean)
- Updated submission routes to save violation flags
- Updated teacher results page to display all violations

### Database Migration
- SQL migration file: `add_violation_flags_migration.sql`
- Auto-migration in `app.py` for SQLite (local development)
- For PostgreSQL (production), run the SQL file manually or use `/dev/migrate_db` route

## Testing

### Local Testing Steps:
1. Start local server: `py run_local.py`
2. Create a quiz as teacher
3. Take quiz as student
4. Try each prohibited shortcut:
   - Press Alt+Tab
   - Press Win+Shift+S
   - Press Win+PrintScreen
   - Press PrintScreen
5. Check teacher results page - violations should be displayed

### Known Limitations:
- **PrintScreen detection** may not work in all browsers due to OS-level handling
- Some browsers may not capture PrintScreen key events
- Alt+Tab detection is most reliable

## Files Modified:
1. `templates/take_shared_quiz.html` - Added keyboard detection
2. `app.py` - Added database columns and backend logic
3. `templates/teacher_results.html` - Display violation flags
4. `add_violation_flags_migration.sql` - Database migration script

## Next Steps:
1. Test locally with all shortcuts
2. Verify violations appear in teacher results
3. If everything works, commit and push to production

