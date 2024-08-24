import click
from .main import BlankSpaceBaby

@click.command()
@click.option('--language', '-l', default='zh', type=click.Choice(['zh', 'en']), help='Main language of the text (zh or en)')
@click.option('--fix-punctuation/--no-fix-punctuation', default=True, help='Fix punctuation based on the main language')
def typeset_text(language, fix_punctuation):
    """Interactive CLI for BlankSpaceBaby text typesetting."""
    click.echo("Welcome to BlankSpaceBaby!")
    click.echo("Enter your text (press Ctrl+D to finish):")
    
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break

    text = '\n'.join(lines)
    
    if not text:
        click.echo("No text entered. Exiting.")
        return

    bsb = BlankSpaceBaby(text, language=language, fix_punctuation=fix_punctuation)
    typeset_text = bsb.typeset()
    
    click.echo("\nTypeset result:")
    click.echo(typeset_text)

if __name__ == '__main__':
    typeset_text()