import {Component, OnInit, signal, WritableSignal} from '@angular/core';
import {FormControl, FormsModule, ReactiveFormsModule} from '@angular/forms';
import {AskService} from '../../../shared/services/ask.service';
import {
    MatCard,
    MatCardContent,
    MatCardHeader,
    MatCardSubtitle,
    MatCardTitle
} from '@angular/material/card';
import {MatDivider} from '@angular/material/divider';
import {MatButton} from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {PdfViewerModule} from 'ng2-pdf-viewer';
import {NgStyle} from '@angular/common';

@Component({
    selector: 'app-user-manuals',
    imports: [
        FormsModule,
        ReactiveFormsModule,
        MatCard,
        MatCardHeader,
        MatProgressSpinnerModule,
        MatCardTitle,
        MatCardSubtitle,
        MatDivider,
        MatCardContent,
        MatButton,
        MatIconModule,
        FontAwesomeModule,
        PdfViewerModule,
        NgStyle
    ],
    templateUrl: './user-manual-assistant.html',
    styleUrl: './user-manual-assistant.scss',
})
export class UserManualAssistant implements OnInit {
    questionForm = new FormControl();
    searchForm = new FormControl();
    selectedManualForm = new FormControl();
    answer: WritableSignal<string> = signal('');
    searchSpinner: WritableSignal<boolean> = signal(false);
    askSpinner: WritableSignal<boolean> = signal(false);
    scrapeSpinner: WritableSignal<boolean> = signal(false);
    uploadStatus: WritableSignal<string> = signal('');
    scrapeStatus: WritableSignal<string> = signal('');
    userManuals: WritableSignal<{title: string, url: string, source: string}[]> = signal([]);
    selectedFile?: File;

    constructor(private askService: AskService) {
    }

    ngOnInit() {
    }

    onSearchManual() {
        this.searchSpinner.set(true);
        this.askService.searchManual(this.searchForm.value).subscribe({
            next: (res: any) => {
                console.log(res);
                this.userManuals.set(res.results);
                this.searchSpinner.set(false);
            },
            error: (err) => {
                console.error('Error:', err);
                this.searchSpinner.set(false);
            },
        });
    }

    onScrapeManual() {
        this.scrapeSpinner.set(true);
        this.scrapeStatus.set('Scraping...');
        this.askService.scrapeManual(this.selectedManualForm.value.url).subscribe({
            next: (res: any) => {
                console.log(res);
                this.scrapeStatus.set(`✅`);
                this.userManuals.set(res.results);
                this.scrapeSpinner.set(false);
            },
            error: (err) => {
                console.error('Error:', err);
                this.scrapeSpinner.set(false);
                this.scrapeStatus.set('❌ Scraping failed.');
            },
        });
    }

    onAsk() {
        this.askSpinner.set(true);
        this.askService.askQuestion(this.questionForm.value).subscribe({
            next: (res) => {
                this.answer.set(res.answer);
                console.log(this.answer);

                this.askSpinner.set(false);
            },
            error: (err) => {
                console.error('Error:', err);
                this.askSpinner.set(false);
            },
        });
    }

    onFileSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            this.selectedFile = input.files[0];
            this.uploadStatus.set(`${this.selectedFile.name} uploaded successfully.`);
        }
    }

    onUpload() {
        if (!this.selectedFile) {
            this.uploadStatus.set('⚠️ Please select a PDF first.');
            return;
        }

        this.uploadStatus.set('Uploading...');
        this.askService.uploadManual(this.selectedFile).subscribe({
            next: (res) => {
                console.log(res);
                this.uploadStatus.set(`✅ ${res.message}`);
            },
            error: (err) => {
                console.error(err);
                this.uploadStatus.set('❌ Upload failed.');
            },
        });
    }
}
