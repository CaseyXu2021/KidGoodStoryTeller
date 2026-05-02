import * as vscode from 'vscode';
import axios from 'axios';

interface WordDefinition {
    word: string;
    phonetic: string;
    meanings: Array<{
        partOfSpeech: string;
        definitions: Array<{
            definition: string;
            example?: string;
        }>;
        synonyms?: string[];
    }>;
    phonetics?: Array<{
        audio?: string;
    }>;
}

export class DictionaryLookup {
    private context: vscode.ExtensionContext;
    private cache: Map<string, WordDefinition> = new Map();
    private readonly API_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en';
    private readonly FALLBACK_API = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json';
    private readonly CACHE_TTL = 3600000; // 1 hour

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.initializeCache();
    }

    private initializeCache() {
        const cachedData = this.context.globalState.get<any>('vocabularyCache') || {};
        this.cache = new Map(Object.entries(cachedData));
    }

    async showDictionary(word: string) {
        const definition = await this.getDefinition(word.toLowerCase());

        if (!definition) {
            vscode.window.showWarningMessage(`Definition not found for "${word}"`);
            return;
        }

        this.displayDefinition(word, definition);
    }

    private async getDefinition(word: string): Promise<WordDefinition | null> {
        // Check cache
        if (this.cache.has(word)) {
            return this.cache.get(word)!;
        }

        try {
            // Try primary API
            const response = await axios.get(`${this.API_URL}/${word}`);
            const definition = response.data[0];
            
            this.cache.set(word, definition);
            this.updateCache();
            
            return definition;
        } catch (error) {
            try {
                // Try fallback API
                const fallbackResponse = await axios.get(`${this.FALLBACK_API}/${word}`);
                if (fallbackResponse.data && fallbackResponse.data.length > 0) {
                    return this.parseFallbackAPI(fallbackResponse.data[0]);
                }
            } catch (fallbackError) {
                console.log(`Could not fetch definition for "${word}"`, error);
            }
            return null;
        }
    }

    private parseFallbackAPI(data: any): WordDefinition {
        return {
            word: data.meta.id,
            phonetic: data.hwi?.prs?.[0]?.mw || '',
            meanings: (data.shortdef || []).map((def: string, index: number) => ({
                partOfSpeech: data.pos?.[index] || 'Definition',
                definitions: [{ definition: def }]
            })),
            phonetics: []
        };
    }

    private displayDefinition(word: string, definition: WordDefinition) {
        const meanings = definition.meanings
            .map(m => `**${m.partOfSpeech}**\n${m.definitions.map(d => `• ${d.definition}`).join('\n')}`)
            .join('\n\n');

        const message = `**${definition.word}** ${definition.phonetic ? `(${definition.phonetic})` : ''}\n\n${meanings}`;

        vscode.window.showInformationMessage(message, 'OK');
    }

    private updateCache() {
        const cacheData = Object.fromEntries(this.cache);
        this.context.globalState.update('vocabularyCache', cacheData);
    }
}
