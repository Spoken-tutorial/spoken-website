import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})

export class CreateScriptService {
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

  // API service for fetching scripts to show in view component
  public getScript(tid, lid, vid) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`
    return this.http.get(_url);
  }

  // API service for creating scripts for the first time
  public postScript(tid, lid, vid, data) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`
    var ls = this.http.post(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

  // API service for updating scripts at slide level
  public patchScript(tid, lid, vid, data) {
    let script_pk = data['id']
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/${script_pk}/`
    var ls = this.http.patch(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

  // API service for deleting scripts at slide level
  public deleteScript(tid, lid, vid, script_pk) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/${script_pk}/`
    var ls = this.http.delete(
      _url,
      this.httpOptions
    );
    return ls;
  }

  public modifyOrdering(script_id, move, slideid) {
    const url = `${this.apiUrl}/scripts/${script_id}/`;

    return this.http.patch(
      url,
      {
        // 'ordering': ordering,
        'slideid': slideid,
        'move': move
      },
      this.httpOptions
    );
  }

  public changeScriptStatus(tid, lid, vid, status) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`

    return this.http.patch(
      _url,
      { 'status': status },
      this.httpOptions
    );
  }

  public getPublishedScripts() {
    const _url = `${this.apiUrl}/scripts/published/`;

    return this.http.get(
      _url
    );
  }

  public getReviewScripts() {
    const _url = `${this.apiUrl}/scripts/review/`;

    return this.http.get(
      _url
    );
  }

  public suggestTutorialTitle(tid, lid, vid, suggested_title) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`
    return this.http.patch(
      _url,
      { 'suggested_title': suggested_title },
      this.httpOptions
    );
  }

  // API service for deleting entire script
  public deleteScriptVersion(tid, lid, vid) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${vid}/`
    var ls = this.http.delete(
      _url,
      this.httpOptions
    );
    return ls;
  }

}
