import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({providedIn: 'root'})
export class AskService {
    private readonly apiUrl = 'http://localhost:8000';

    constructor(private http: HttpClient) {
    }

    askQuestion(question: string): Observable<{ answer: string }> {
        return this.http.post<{ answer: string }>(`${this.apiUrl}/ask`, {question});
    }

    searchManual(searchTerm: string) {
        return this.http.post<{ model: string }>(`${this.apiUrl}/search/manuals`, {model: searchTerm});
    }

    scrapeManual(manualUrl: string) {
        return this.http.post<{ url: string }>(`${this.apiUrl}/scrape/manual`, {url: manualUrl});
    }

    uploadManual(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<{ message: string }>(
            `${this.apiUrl}/upload`,
            formData
        );
    }

}
