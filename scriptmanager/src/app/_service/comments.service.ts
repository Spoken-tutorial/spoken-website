import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})
export class CommentsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']

  public getComment(tid){
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    return this.httpClient.get(_url);
  }

  public postComment(tid,data) {
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    var ls = this.httpClient.post(
      _url,
      data
    );
    return ls;
  }

  constructor(private httpClient: HttpClient) { }
}
