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
    // inserting CSRF token in the http headers
    let csrf = this._cookieService.get("csrftoken");
    if (typeof (csrf) === 'undefined') {
      csrf = '';
    }
    this.httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json', 'X-CSRFToken': csrf })
    };
  }

  // API service for fetching comments to show in view component
  public getComment(tid){
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    return this.http.get(_url);
  }

  // API service for creating comments.
  public postComment(tid,data) {
    const _url = `${this.apiUrl}/scripts/${tid}/comments/`
    var ls = this.http.post(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

  public modifyComment(cid, data) {
    const url = `${this.apiUrl}/comments/${cid}/`;

    return this.http.patch(
      url,
      data,
      this.httpOptions
    );
  }

  public deleteComment(cid) {
    const url = `${this.apiUrl}/comments/${cid}/`;

    return this.http.delete(
      url,
      this.httpOptions
    );
  }

  public changeCommentDoneStatus(cid, status) {
    const url = `${this.apiUrl}/comments/${cid}/`;

    return this.http.patch(
      url,
      { 'done': status },
      this.httpOptions
    );
  }

  public changeCommentResolvedStatus(cid, status) {
    const url = `${this.apiUrl}/comments/${cid}/`;

    return this.http.patch(
      url,
      { 'resolved': status },
      this.httpOptions
    );
  }

}
