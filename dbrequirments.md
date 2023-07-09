-- Enable the pgvector extension to work with embedding vectors
create extension vector;

-- Create a table to store your documents
create table rules (
  id uuid primary key,
  content text, -- corresponds to Document.pageContent
  metadata jsonb, -- corresponds to Document.metadata
  embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
);

-- Create a function to similarity search for documents
create function match_rules (
  query_embedding vector(1536),
  match_count int,
  filter jsonb DEFAULT '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (rules.embedding <=> query_embedding) as similarity
  from rules
  where metadata @> filter
  order by rules.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Create a function to keyword search for documents
create function kw_match_rules(query_text text, match_count int)
returns table (id uuid, content text, metadata jsonb, similarity real)
as $$

begin
return query execute
format('select id, content, metadata, ts_rank(to_tsvector(content), plainto_tsquery($1)) as similarity
from rules
where to_tsvector(content) @@ plainto_tsquery($1)
order by similarity desc
limit $2')
using query_text, match_count;
end;
$$ language plpgsql;


--------------------------------------


-- Create a table to store your documents
create table cards (
  id uuid primary key,
  content text, -- corresponds to Document.pageContent
  metadata jsonb, -- corresponds to Document.metadata
  embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
);

-- Create a function to similarity search for documents
create function match_cards (
  query_embedding vector(1536),
  match_count int,
  filter jsonb DEFAULT '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (cards.embedding <=> query_embedding) as similarity
  from cards
  where metadata @> filter
  order by cards.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Create a function to keyword search for documents
create function kw_match_cards(query_text text, match_count int)
returns table (id uuid, content text, metadata jsonb, similarity real)
as $$

begin
return query execute
format('select id, content, metadata, ts_rank(to_tsvector(content), plainto_tsquery($1)) as similarity
from cards
where to_tsvector(content) @@ plainto_tsquery($1)
order by similarity desc
limit $2')
using query_text, match_count;
end;
$$ language plpgsql;