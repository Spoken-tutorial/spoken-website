import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

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
  constructor(private http: HttpClient) { }
}
