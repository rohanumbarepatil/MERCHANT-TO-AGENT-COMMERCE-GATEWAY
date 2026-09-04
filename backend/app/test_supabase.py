from app.database.client import supabase


response = supabase.table("merchants").select("*").execute()

print("Supabase connection successful!")
print(response.data)