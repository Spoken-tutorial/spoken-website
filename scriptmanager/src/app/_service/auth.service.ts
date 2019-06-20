import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

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
