import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})
export class RevisionsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']

  public getRevisions(sid){
    const _url = `${this.apiUrl}/scripts/${sid}/reversions/`
    return this.httpClient.get(_url);
  }
  

  constructor(private httpClient: HttpClient) { }
}
