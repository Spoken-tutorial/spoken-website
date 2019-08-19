import { Component, HostListener } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { routerTransition } from './animations';
import { AuthService } from './_service/auth.service';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass'],
  animations: [
    routerTransition
  ]
})
export class AppComponent {
  title = 'scriptmanager';

  constructor(private authService: AuthService) {
    if (environment.production == false) {
      // when we are working on the angular Server, we have to make an api call to get the jwt token and we are storing 
      // that token in localstorage
      this.authService.getJwtToken().subscribe(
        (res) => {
          localStorage.setItem('token', res['token'])
        },
        (err) => console.error('Failed to fetch JWT token')
      );
    }
  }

  prepareRoute(outlet: RouterOutlet) {
    return outlet && outlet.activatedRouteData && outlet.activatedRouteData['animation'];
  }

  ngOnInit(): void {

  }

}
