from flatten_codebase import flatten_codebase

prompt = """
### CONTEXT
You are an expert technical writer building developer documentation for a production Python micro-service.  
Audience: experienced Python developers new to the codebase.  
Output format: valid Markdown files compatible with MkDocs & mkdocstrings (Material theme).  
Code style: Google-style docstrings.

### DELIVERABLE
Return a **ZIP-like listing** of Markdown files whose content is fully written out, for example:

docs/
  index.md
  architecture.md
  flow.md
  configuration.md
  deployment.md
  troubleshooting.md
  reference.md  (contains only mkdocstrings directives)

For each file include the full Markdown text.  
Inside `reference.md`, place one line per public package path in the form:

    ::: scheduler_service.<module>[.<submodule>]

Do **not** repeat code in prose—link or reference it.  
Keep each page concise (< 150 lines) and use the following style hints:

* Use level-2 headings (`##`) for main sections, level-3 for subsections.
* Prefer bullet lists over paragraphs where possible.
* Wrap explanatory call-outs in admonitions (`!!! tip`, `!!! warning`, etc.).
* For diagrams embed Mermaid fenced blocks when a sequence or component diagram clarifies flow.
* Cross-link pages using relative links (e.g. `[Architecture](architecture.md)`).
* Assume MkDocs extensions: `pymdownx.superfences`, `admonition`, `details`, `highlight`.

### INPUT CODE BASE
{code_source}
"""
filled_prompt = prompt.format(code_source=flatten_codebase("./src/")) 
