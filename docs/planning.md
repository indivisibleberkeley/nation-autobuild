# Design / implementation plan

## Envisioned workflow

### First Page

1. Form with file upload field
2. User uploads SignUpGenius CSV
3. Store file in database with auto-generated unique key
4. Redirect to next page

### Second Page

1. Read column headers from CSV
2. Have user select which column is Email, Role, and Date
3. Store column mappings in database
4. Redirect to next page

### Third Page

1. Read unique (lowercased) entries in Role column
2. Ask user to match each entry with a tag from a pre-determined list
3. Store role-tag mappings in database
4. Redirect to next page

### Fourth Page

1. Display each unique email with the list of unique month/role tags computed for it
2. Provide link to download the CSV
3. Keep the final CSV in the database so that it can be downloaded again later

## Required software

1. Python
2. Flask (web framework)
3. MongoDB (database)
4. GUnicorn (app server)
