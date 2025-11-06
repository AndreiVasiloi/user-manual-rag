import {Component} from '@angular/core';
import {UserManualAssistant} from './features/user-manual-assistant/user-manual-assistant';

@Component({
    selector: 'app-root',
    imports: [
        UserManualAssistant
    ],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {

}
