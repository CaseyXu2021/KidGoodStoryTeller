import * as vscode from 'vscode';

interface DecorationType {
    [key: string]: vscode.TextEditorDecorationType;
}

export class VocabularyHighlighter {
    private nounDecoration: vscode.TextEditorDecorationType;
    private verbDecoration: vscode.TextEditorDecorationType;
    private adverbDecoration: vscode.TextEditorDecorationType;
    private context: vscode.ExtensionContext;

    // Pattern mapping for POS tagging
    private nounPatterns = [
        /\b(boy|girl|child|man|woman|person|student|teacher|doctor|nurse|cat|dog|bird|tree|flower|house|city|country|school|book|story|adventure|journey|dragon|wizard|princess|prince|magic|spell|power|sword|treasure|island|mountain|valley|river|ocean|sky|star|moon|sun|wind|rain|snow|fire|water|stone|gold|silver|diamond)\b/gi
    ];

    private verbPatterns = [
        /\b(is|are|was|were|be|have|has|had|do|does|did|go|went|come|came|see|saw|look|looked|find|found|take|took|make|made|give|gave|tell|told|ask|said|know|knew|think|thought|want|wanted|get|got|use|used|find|found|try|tried|leave|left|put|put|mean|meant|keep|kept|help|helped|show|showed|hear|heard|let|let|begin|began|seem|seemed|help|helped|talk|talked|turn|turned|start|started|move|moved|jump|jumped|run|ran|walk|walked|fly|flew|swim|swam|dance|danced|sing|sang|play|played|laugh|laughed|cry|cried)\b/gi
    ];

    private adverbPatterns = [
        /\b(very|really|quite|rather|fairly|pretty|much|more|most|less|least|even|just|only|also|too|well|badly|quickly|slowly|carefully|easily|happily|sadly|suddenly|finally|finally|always|never|sometimes|often|usually|seldom|hardly|scarcely|almost|almost|completely|entirely|absolutely|perfectly|totally|fully)\b/gi
    ];

    constructor(context: vscode.ExtensionContext) {
        this.context = context;

        // Noun decoration - Green bubbles
        this.nounDecoration = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(46,204,113,0.25)',
            border: '1px solid #2ecc71',
            borderRadius: '3px',
            cursor: 'pointer',
            fontWeight: 'bold'
        });

        // Verb decoration - Red bubbles
        this.verbDecoration = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(231,76,60,0.25)',
            border: '1px solid #e74c3c',
            borderRadius: '3px',
            cursor: 'pointer',
            fontWeight: 'bold'
        });

        // Adverb decoration - Yellow bubbles
        this.adverbDecoration = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(241,196,15,0.25)',
            border: '1px solid #f1c40f',
            borderRadius: '3px',
            cursor: 'pointer',
            fontWeight: 'bold'
        });
    }

    highlightVocabulary(editor: vscode.TextEditor) {
        const text = editor.document.getText();
        
        // Find all ranges
        const nouns = this.findMatches(text, this.nounPatterns);
        const verbs = this.findMatches(text, this.verbPatterns);
        const adverbs = this.findMatches(text, this.adverbPatterns);

        // Apply decorations
        editor.setDecorations(this.nounDecoration, nouns);
        editor.setDecorations(this.verbDecoration, verbs);
        editor.setDecorations(this.adverbDecoration, adverbs);
    }

    private findMatches(text: string, patterns: RegExp[]): vscode.Range[] {
        const ranges: vscode.Range[] = [];

        for (const pattern of patterns) {
            let match;
            const regex = new RegExp(pattern.source, pattern.flags);
            
            while ((match = regex.exec(text)) !== null) {
                const startPos = match.index;
                const endPos = startPos + match[0].length;

                const startLine = text.substring(0, startPos).split('\n').length - 1;
                const lineText = text.split('\n')[startLine];
                const startChar = startPos - text.substring(0, startPos).lastIndexOf('\n') - 1;
                const endChar = startChar + match[0].length;

                const range = new vscode.Range(
                    new vscode.Position(startLine, startChar),
                    new vscode.Position(startLine, endChar)
                );

                ranges.push(range);
            }
        }

        return this.removeDuplicates(ranges);
    }

    private removeDuplicates(ranges: vscode.Range[]): vscode.Range[] {
        const seen = new Set<string>();
        return ranges.filter(range => {
            const key = `${range.start.line}-${range.start.character}-${range.end.character}`;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
}
