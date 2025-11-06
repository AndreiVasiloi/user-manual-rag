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
import { faRobot } from '@fortawesome/free-solid-svg-icons';

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
        FontAwesomeModule
    ],
    templateUrl: './user-manual-assistant.html',
    styleUrl: './user-manual-assistant.scss',
})
export class UserManualAssistant implements OnInit {
    questionForm = new FormControl();
    answer: WritableSignal<string> = signal('');
    loading = false;
    uploadStatus: WritableSignal<string> = signal('');
    selectedFile?: File;

    constructor(private askService: AskService) {
    }

    ngOnInit() {
        this.questionForm.valueChanges.subscribe(res => console.log(res));
    }

    onAsk() {
        this.loading = true;
        this.askService.askQuestion(this.questionForm.value).subscribe({
            next: (res) => {
                this.answer.set(res.answer);
                console.log(this.answer);

                this.loading = false;
            },
            error: (err) => {
                console.error('Error:', err);
                this.loading = false;
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

    protected readonly faRobot = faRobot;
}
