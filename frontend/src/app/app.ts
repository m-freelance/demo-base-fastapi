import {Component, computed, inject} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {AuthService} from './services';
import {Header} from './components/header/header';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  private readonly authService = inject(AuthService);
  readonly isAuthenticated = computed(() => this.authService.isAuthenticated());

}
