preview:
    quarto preview --port 4444

publish:
    quarto render
    quarto publish netlify

new-post filename:
    mkdir posts/{{filename}}
    touch posts/{{filename}}/index.md
    echo "---\ndate: \"$(date +%Y-%m-%d)\"\ntitle: \"\"\ncategories: []\n---" > posts/{{filename}}/index.md
    code posts/{{filename}}/index.md