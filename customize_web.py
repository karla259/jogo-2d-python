from pathlib import Path

index = Path('build/web/index.html')
if not index.exists():
    raise SystemExit('build/web/index.html não foi encontrado')

html = index.read_text(encoding='utf-8')

# Fundo padrão cinza do Pygbag -> fundo do jogo.
html = html.replace(
    'platform.document.body.style.background = "#7f7f7f"',
    'platform.document.body.style.background = "#0d1736"'
)
html = html.replace('Loading, please wait ...', 'Carregando Aventura dos Cristais...')
html = html.replace('Loading, please wait...', 'Carregando Aventura dos Cristais...')

css = r'''<style id="aventura-mobile-style">
html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  min-height: 100% !important;
  background: radial-gradient(circle at 50% 30%, #203f86 0%, #0d1736 55%, #080d20 100%) !important;
  overflow: hidden !important;
}
body {
  min-height: 100vh !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  touch-action: none !important;
}
canvas {
  display: block !important;
  width: min(100vw, 177.777vh) !important;
  height: min(56.25vw, 100vh) !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
  margin: auto !important;
  background: #0d1736 !important;
  image-rendering: auto !important;
  touch-action: none !important;
}
#transfer, #status, #progress, progress {
  border-radius: 16px !important;
}
</style>'''

if 'aventura-mobile-style' not in html:
    if '</head>' in html:
        html = html.replace('</head>', css + '\n</head>', 1)
    else:
        pos = html.find('>')
        if pos != -1:
            html = html[:pos + 1] + '\n' + css + html[pos + 1:]
        else:
            html = css + html

index.write_text(html, encoding='utf-8')
print('Tela web personalizada com sucesso.')
