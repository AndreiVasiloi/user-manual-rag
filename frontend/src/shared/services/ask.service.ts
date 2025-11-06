import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({providedIn: 'root'})
export class AskService {
    private readonly apiUrl = 'http://localhost:8000/ask';

    constructor(private http: HttpClient) {
    }

    askQuestion(question: string): Observable<{ answer: string }> {
        return this.http.post<{ answer: string }>(this.apiUrl, {question});
    }

    uploadManual(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<{ message: string }>(
            'http://localhost:8000/upload',
            formData
        );
    }

}
