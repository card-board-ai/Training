import os
import configparser
from supabase.client import Client, create_client

local_supabase_url = "http://localhost:54321"
local_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
prod_supabase_url = "https://tzrsrwethpgxfeukzgkw.supabase.co"
prod_supabase_private_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6cnNyd2V0aHBneGZldWt6Z2t3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4MjEzNzcwOSwiZXhwIjoxOTk3NzEzNzA5fQ.MjUipkQNje2SIFGDZTjyicFjsfH1GME2PPlkrV8FdqI"
supabase: Client = create_client(prod_supabase_url, prod_supabase_private_key)
config = configparser.ConfigParser()
config.read('keys.cfg')

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore