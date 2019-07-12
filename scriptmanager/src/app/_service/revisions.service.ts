import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})
export class RevisionsService {
  public env = environment;
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

  // API service for fetching all revisions for a particular slide ID
  public getRevisions(sid) {
    const _url = `${this.apiUrl}/scripts/${sid}/reversions/`
    return this.http.get(_url);
  }

  // API service for reverting back to the provided revision id
  public revertRevision(sid, rid) {
    const _url = `${this.apiUrl}/scripts/${sid}/reversions/${rid}/`
    var ls = this.http.patch(
      _url,
      {},
      this.httpOptions
    );
    return ls;
  }
}
