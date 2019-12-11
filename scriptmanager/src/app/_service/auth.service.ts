import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { JwtHelperService } from "@auth0/angular-jwt";

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  jwtHelper = new JwtHelperService();

  // using JwtToken for authorization purpose in angular system. Nothing to do with main django system.
  public getJwtToken() {
    return this.http.post(
      'http://localhost:8000/api-token-auth/',
      {
        'username': 'admin',
        'password': 'test123'
      }
    );
  }

  public isAuthenticated() {
    const token = this.getToken();
    if (token === '') return false;
    
    return !this.jwtHelper.isTokenExpired(token);
  }

  public getToken() {
    const token = localStorage.getItem('token');
    return token;
  }

  public isReviewer() {
    if (this.isAuthenticated()) {
      const token = this.getToken();
      const decodedToken = this.jwtHelper.decodeToken(token);
      return decodedToken['is_domainreviewer'] || decodedToken['is_videoreviewer'];
    }

    return false;
  }

  public isOwner(user) {
    if (this.getToken() === '')
      return false;

    const decodedToken = this.jwtHelper.decodeToken(this.getToken());
    return decodedToken['username'] === user;
  }
  constructor(private http: HttpClient) { }
}
