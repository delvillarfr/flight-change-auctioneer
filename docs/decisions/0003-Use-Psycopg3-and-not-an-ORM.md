# Use Psycopg3 and not an ORM

An ORM allows me to interact with databases using native python objects.
In Psycopg3, I interact with them through SQL.

I prefer to use SQL directly.

## SQL is general-purpose; ORMs are special-purpose

Every major programming language has an adapter to interact with databases through SQL.
If I know SQL, I can work with databases in any language with a similar interface.
In contrast, the interfaces of ORMs are all different and specific to a programming language.

## ORMs use SQL

They map commands into SQL to communicate with databases.
By using SQL directly, I avoid many dependencies.

## SQL is a prerequisite to ORMs

To use an ORM well, I must understand how it maps my commands to SQL.
If I don't know SQL, I cannot.
