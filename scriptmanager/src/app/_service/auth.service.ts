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
    this.getToken();
    this.isVideoReviewer();
    return this.http.post(
      'http://localhost:8000/api-token-auth/',
      {
        'username': 'admin',
        'password': 'test123'
      }
    );
  }

  public getToken() {
    const token = localStorage.getItem('token');
    console.log(token);
    return token;
  }

  public isVideoReviewer() {
    const token = this.getToken();
    const decodedToken = this.jwtHelper.decodeToken(token);
    console.log(decodedToken);
    return true;
  }
  constructor(private http: HttpClient) { }
}
