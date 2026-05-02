import * as vscode from 'vscode';
import { VocabularyHighlighter } from './vocabularyHighlighter';
import { DictionaryLookup } from './dictionaryLookup';

let vocabularyHighlighter: VocabularyHighlighter;
let dictionaryLookup: DictionaryLookup;

export function activate(context: vscode.ExtensionContext) {
    console.log('Story Vocabulary Extension activated!');

    // Initialize highlighter and dictionary lookup
    vocabularyHighlighter = new VocabularyHighlighter(context);
    dictionaryLookup = new DictionaryLookup(context);

    // Register command
    let highlightCommand = vscode.commands.registerCommand(
        'story-vocab-extension.highlightVocabulary',
        () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                vocabularyHighlighter.highlightVocabulary(editor);
            }
        }
    );

    context.subscriptions.push(highlightCommand);

    // Auto-highlight on file open
    vscode.workspace.onDidOpenTextDocument((document) => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document === document) {
            vocabularyHighlighter.highlightVocabulary(editor);
        }
    });

    // Auto-highlight on text change (debounced)
    let highlightTimeout: NodeJS.Timeout;
    vscode.workspace.onDidChangeTextDocument((event) => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document === event.document) {
            clearTimeout(highlightTimeout);
            highlightTimeout = setTimeout(() => {
                vocabularyHighlighter.highlightVocabulary(editor);
            }, 500);
        }
    });

    // Dictionary lookup on double-click
    vscode.window.onDidChangeTextEditorSelection((event) => {
        const editor = event.textEditor;
        const selection = editor.selection;

        if (!selection.isEmpty) {
            const selectedText = editor.document.getText(selection);
            // Simple word boundary check
            if (/^[a-zA-Z]+$/.test(selectedText) && selectedText.length > 2) {
                dictionaryLookup.showDictionary(selectedText);
            }
        }
    });
}

export function deactivate() {
    console.log('Story Vocabulary Extension deactivated!');
}
