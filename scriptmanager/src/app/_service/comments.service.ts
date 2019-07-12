import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})
export class CommentsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']
  private httpOptions: any;

  constructor(private http: HttpClient, private _cookieService: CookieService) {
    let csrf = this._cookieService.get("csrftoken");
    if (typeof (csrf) === 'undefined') {
      csrf = '';
    }
    this.httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json', 'X-CSRFToken': csrf })
    };
  }
  public getComment(tid){
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    return this.http.get(_url);
  }

  public postComment(tid,data) {
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    var ls = this.http.post(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

}
