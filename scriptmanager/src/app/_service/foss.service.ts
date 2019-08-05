import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})



export class FossService {
  public env = environment;
  public apiUrl = this.env['apiUrlScript'];
  public currentFossCategory = -1;
  public currentFossCategoryLanguage = -1;

  // API service for fetching all foss categories assigned to the logged in user
  public getAllFossCategories() {
    return this.httpClient.get(`${this.apiUrl}/foss/`);
  }

  constructor(private httpClient: HttpClient) { }


}